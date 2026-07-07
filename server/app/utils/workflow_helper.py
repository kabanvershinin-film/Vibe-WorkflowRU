import os
import httpx
import logging
from fastapi import HTTPException
from typing import Optional
from pathlib import Path
from ..config import settings

BASE_DIR = Path(__file__).resolve().parent.parent.parent
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_api_key():
    if settings.PROVIDER == "grsai":
        api_key = settings.GRSAI_API_KEY
    else:
        api_key = settings.MU_API_KEY
    if not api_key:
        raise HTTPException(status_code=400, detail=f"Setup {settings.PROVIDER.upper()}_API_KEY in .env to use {settings.PROVIDER} provider")
    return api_key

async def proxy_request_helper(method: str, url: str, payload: Optional[dict] = None):
    api_key = await get_api_key()
    
    if settings.PROVIDER == "grsai":
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
    else:
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
        }

    async with httpx.AsyncClient() as client:
        try:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers, timeout=60.0)
            elif method.upper() == "POST":
                response = await client.post(url, json=payload, headers=headers, timeout=60.0)
            elif method.upper() == "DELETE":
                response = await client.delete(url, headers=headers, timeout=60.0)
            else:
                raise HTTPException(status_code=405, detail=f"Method {method} not supported in proxy")

        except httpx.RequestError as e:
            logger.error(f"HTTPExt Request Error for {method} {url}: {e}")
            raise HTTPException(status_code=500, detail=f"Error contacting remote server: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in proxy_request_helper for {method} {url}: {e}")
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

    try:
        if response.content:
            resp_json = response.json()
        else:
            resp_json = {}
    except ValueError:
        resp_json = {"detail": response.text or "Unknown error from remote server"}

    if response.status_code == 200:
        return resp_json
    else:
        error_detail = resp_json.get("detail", "Something went wrong")
        logger.warning(f"Remote server returned {response.status_code}: {error_detail}")
        raise HTTPException(status_code=response.status_code, detail=error_detail)

async def run_grsai_node_helper(payload: dict):
    """
    Handle GRSai API node directly (gpt-image-2, gpt-image-2-vip, Nano Banana)
    """
    params = payload.get("params", {})
    
    base_url = params.get("base_url", settings.GRSAI_BASE_URL.replace("https://", ""))
    api_key = params.get("api_key", settings.GRSAI_API_KEY)
    model = params.get("model")
    prompt = params.get("prompt")
    images = params.get("images", [])
    aspect_ratio = params.get("aspectRatio", "1024x1024")
    reply_type = params.get("replyType", "json")

    if not api_key:
        raise HTTPException(status_code=400, detail="GRSai API key is required")
    if not model:
        raise HTTPException(status_code=400, detail="Model is required")
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")

    url = f"https://{base_url}/v1/api/generate"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    grsai_payload = {
        "model": model,
        "prompt": prompt,
        "images": images,
        "aspectRatio": aspect_ratio,
        "replyType": reply_type
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=grsai_payload, headers=headers, timeout=120.0)
        except httpx.RequestError as e:
            logger.error(f"GRSai Request Error: {e}")
            raise HTTPException(status_code=500, detail=f"Error contacting GRSai: {str(e)}")

    try:
        resp_json = response.json()
    except ValueError:
        raise HTTPException(status_code=500, detail=f"Invalid response from GRSai: {response.text}")

    if response.status_code != 200:
        error_detail = resp_json.get("error", str(resp_json))
        raise HTTPException(status_code=response.status_code, detail=f"GRSai error: {error_detail}")

    # Convert GRSai response to workflow output format
    outputs = []
    if resp_json.get("status") == "succeeded":
        for result in resp_json.get("results", []):
            if result.get("url"):
                outputs.append({
                    "type": "image",
                    "value": result["url"]
                })
    elif resp_json.get("status") == "failed":
        error_msg = resp_json.get("error", "Unknown error from GRSai")
        raise HTTPException(status_code=400, detail=error_msg)

    return {
        "status": "succeeded",
        "outputs": outputs,
        "grsai_response": resp_json
    }

async def create_or_update_workflow(payload: dict):
    if settings.PROVIDER == "grsai":
        # Mock GRSai create workflow (or use your own endpoints)
        return {
            "id": "demo",
            "name": payload.get("name", "Demo Workflow"),
            "nodes": payload.get("nodes", []),
            "edges": payload.get("edges", [])
        }
    url = f"{settings.MU_API_BASE}/workflow/create"
    return await proxy_request_helper("POST", url, payload)

async def get_node_schemas_helper(workflow_id: str):
    if settings.PROVIDER == "grsai":
        # Mock node schemas for GRSai
        return {
            "image_models": [
                {"id": "image-passthrough", "name": "Input Image", "input_params": {"properties": {"image_url": {"type": "string"}}, "required": []}},
                {"id": "nano-banana", "name": "Nano Banana", "input_params": {"properties": {"prompt": {"type": "string"}}, "required": ["prompt"]}},
            ],
            "video_models": [],
            "text_models": [{"id": "text-passthrough", "name": "Input Text", "input_params": {"properties": {"prompt": {"type": "string"}}, "required": []}}],
            "audio_models": [],
            "concat_models": [{"id": "prompt-concatenator", "name": "Prompt Concatenator", "input_params": {"properties": {"prompt": {"type": "string"}}, "required": []}}],
            "video_combiner_models": []
        }
    url = f"{settings.MU_API_BASE}/workflow/{workflow_id}/node-schemas"
    return await proxy_request_helper("GET", url)

async def get_api_node_schemas_helper(workflow_id: str):
    if settings.PROVIDER == "grsai":
        # Mock API node schemas for GRSai
        return {
            "api_node_models": [
                {"id": "grsai", "name": "GRSai API", "input_params": {"properties": {
                    "base_url": {"type": "string", "default": settings.GRSAI_BASE_URL.replace("https://", "")},
                    "api_key": {"type": "string"},
                    "model": {"type": "string", "enum": ["gpt-image-2", "gpt-image-2-vip"], "default": "gpt-image-2"},
                    "prompt": {"type": "string"},
                    "images": {"type": "array", "default": []},
                    "aspectRatio": {"type": "string", "default": "1024x1024"},
                    "replyType": {"type": "string", "enum": ["json", "stream", "async"], "default": "json"},
                }, "required": ["model", "prompt"]}}
            ]
        }
    url = f"{settings.MU_API_BASE}/workflow/{workflow_id}/api-node-schemas"
    return await proxy_request_helper("GET", url)

async def get_workflow_def_helper(workflow_id: str):
    if settings.PROVIDER == "grsai":
        # Mock workflow def for GRSai
        return {
            "id": "demo",
            "name": "Demo Workflow",
            "nodes": [],
            "edges": [],
            "data": {"nodes": []}
        }
    url = f"{settings.MU_API_BASE}/workflow/get-workflow-def/{workflow_id}"
    return await proxy_request_helper("GET", url)

async def get_workflow_defs_helper():
    if settings.PROVIDER == "grsai":
        # Mock workflows for GRSai
        return []
    url = f"{settings.MU_API_BASE}/workflow/get-workflow-defs"
    return await proxy_request_helper("GET", url)

async def delete_workflow_def_by_id(workflow_id: str):
    if settings.PROVIDER == "grsai":
        return {"status": "ok"}
    url = f"{settings.MU_API_BASE}/workflow/delete-workflow-def/{workflow_id}"
    return await proxy_request_helper("DELETE", url)

async def update_workflow_name_helper(workflow_id: str, payload: dict):
    if settings.PROVIDER == "grsai":
        return {"id": workflow_id, "name": payload.get("name", "Demo")}
    url = f"{settings.MU_API_BASE}/workflow/update-name/{workflow_id}"
    return await proxy_request_helper("POST", url, payload)

async def run_workflow_helper(workflow_id: str, payload: dict):
    if settings.PROVIDER == "grsai":
        # Mock run workflow for GRSai
        return {"run_id": "demo-run-1"}
    url = f"{settings.MU_API_BASE}/workflow/{workflow_id}/run"
    return await proxy_request_helper("POST", url, payload)

async def get_run_status_helper(run_id: str):
    if settings.PROVIDER == "grsai":
        # Mock run status for GRSai
        return {"nodes": {}}
    url = f"{settings.MU_API_BASE}/workflow/run/{run_id}/status"
    return await proxy_request_helper("GET", url)

async def run_node_helper(workflow_id: str, node_id: str, payload: dict):
    # Check if this is a GRSai node and handle directly
    if payload.get("model") == "grsai":
        return await run_grsai_node_helper(payload)
    
    # If provider is GRSai, and model is image model, use GRSai as fallback
    if settings.PROVIDER == "grsai" and payload.get("model"):
        # Wrap the payload into GRSai node
        grsai_payload = {
            "model": "grsai",
            "params": {
                "model": "gpt-image-2",
                "prompt": payload.get("params", {}).get("prompt", "test"),
                "base_url": settings.GRSAI_BASE_URL.replace("https://", ""),
                "api_key": settings.GRSAI_API_KEY,
            }
        }
        return await run_grsai_node_helper(grsai_payload)
    
    # Otherwise proxy to muapi.ai
    url = f"{settings.MU_API_BASE}/workflow/{workflow_id}/node/{node_id}/run"
    return await proxy_request_helper("POST", url, payload)

async def publish_workflow_helper(workflow_id: str, payload: dict):
    if settings.PROVIDER == "grsai":
        return {"status": "ok"}
    url = f"{settings.MU_API_BASE}/workflow/workflow/{workflow_id}/publish"
    return await proxy_request_helper("POST", url, payload)

async def template_workflow_helper(workflow_id: str, payload: dict):
    if settings.PROVIDER == "grsai":
        return {"status": "ok"}
    url = f"{settings.MU_API_BASE}/workflow/workflow/{workflow_id}/template"
    return await proxy_request_helper("POST", url, payload)

async def cloudfront_signed_url_helper(payload: dict):
    if settings.PROVIDER == "grsai":
        return {"signed_url": payload.get("url", "")}
    url = f"{settings.MU_API_BASE}/workflow/cloudfront-signed-url"
    return await proxy_request_helper("POST", url, payload)

async def generate_thumbnail_helper(workflow_id: str, payload: dict):
    if settings.PROVIDER == "grsai":
        return {"status": "ok"}
    url = f"{settings.MU_API_BASE}/workflow/{workflow_id}/thumbnail"
    return await proxy_request_helper("POST", url, payload)

async def get_file_upload_url_helper(params: dict):
    if settings.PROVIDER == "grsai":
        return {"url": ""}
    import urllib.parse
    query_string = urllib.parse.urlencode(params)
    url = f"{settings.MU_API_BASE}/app/get_file_upload_url?{query_string}"
    return await proxy_request_helper("GET", url)

async def get_workflow_last_run(workflow_id: str):
    if settings.PROVIDER == "grsai":
        return None
    url = f"{settings.MU_API_BASE}/workflow/get-workflow-last-run/{workflow_id}"
    return await proxy_request_helper("GET", url)

async def architect_workflow_helper(payload: dict):
    if settings.PROVIDER == "grsai":
        return {"id": "demo-architect-1"}
    url = f"{settings.MU_API_BASE}/workflow/architect"
    return await proxy_request_helper("POST", url, payload)

async def poll_architect_result_helper(id: str):
    if settings.PROVIDER == "grsai":
        return {"status": "ok"}
    url = f"{settings.MU_API_BASE}/workflow/poll-architect/{id}/result"
    return await proxy_request_helper("GET", url)

async def delete_node_run_by_id_helper(node_run_id: str):
    if settings.PROVIDER == "grsai":
        return {"status": "ok"}
    url = f"{settings.MU_API_BASE}/workflow/node-run/{node_run_id}"
    return await proxy_request_helper("DELETE", url)

async def update_workflow_category_helper(workflow_id: str, payload: dict):
    if settings.PROVIDER == "grsai":
        return {"status": "ok"}
    url = f"{settings.MU_API_BASE}/workflow/update-category/{workflow_id}"
    return await proxy_request_helper("POST", url, payload)

async def get_workflow_api_inputs_helper(workflow_id: str):
    if settings.PROVIDER == "grsai":
        return {}
    url = f"{settings.MU_API_BASE}/workflow/{workflow_id}/api-inputs"
    return await proxy_request_helper("GET", url)

async def execute_workflow_via_api_helper(workflow_id: str, payload: dict):
    if settings.PROVIDER == "grsai":
        return {"status": "ok"}
    url = f"{settings.MU_API_BASE}/workflow/{workflow_id}/api-execute"
    return await proxy_request_helper("POST", url, payload)

async def get_workflow_api_outputs_helper(run_id: str):
    if settings.PROVIDER == "grsai":
        return {}
    url = f"{settings.MU_API_BASE}/workflow/run/{run_id}/api-outputs"
    return await proxy_request_helper("GET", url)
