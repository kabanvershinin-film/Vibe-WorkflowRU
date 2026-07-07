import React from 'react';
import { cookies } from "next/headers";
import WorkflowBuilderClient from "./WorkflowBuilderClient";

// Моковые данные для демо-режима
const mockWorkflowData = {
  id: "demo",
  name: "Demo Workflow",
  nodes: [
    { id: "text-node-1", type: "textNode", position: { x: 100, y: 100 }, data: { prompt: "A cute dog", selectedModel: { id: "text-passthrough", name: "Input Text" } } },
    { id: "image-node-1", type: "imageNode", position: { x: 400, y: 100 }, data: { prompt: "A cute dog", selectedModel: { id: "nano-banana", name: "Nano Banana" } } },
  ],
  edges: [
    { id: "e1-2", source: "text-node-1", sourceHandle: "textOutput", target: "image-node-1", targetHandle: "textInput" },
  ],
  data: { nodes: [], interactionMode: true, publishWorkflow: false },
};

// Моковые схемы нод
const mockNodeSchemas = {
  image_models: [
    { id: "image-passthrough", name: "Input Image", input_params: { properties: { "image_url": { type: "string" } }, required: [] } },
    { id: "nano-banana", name: "Nano Banana", input_params: { properties: { "prompt": { type: "string" } }, required: ["prompt"] } },
    { id: "flux-schnell", name: "Flux Schnell", input_params: { properties: { "prompt": { type: "string" } }, required: ["prompt"] } },
  ],
  video_models: [
    { id: "video-passthrough", name: "Input Video", input_params: { properties: { "video_url": { type: "string" } }, required: [] } },
    { id: "seedance-lite-t2v", name: "Seedance Lite T2V", input_params: { properties: { "prompt": { type: "string" } }, required: ["prompt"] } },
    { id: "seedance-pro-t2v", name: "Seedance Pro T2V", input_params: { properties: { "prompt": { type: "string" } }, required: ["prompt"] } },
    { id: "seedance-v1.5-pro-t2v", name: "Seedance v1.5 Pro T2V", input_params: { properties: { "prompt": { type: "string" } }, required: ["prompt"] } },
  ],
  text_models: [
    { id: "text-passthrough", name: "Input Text", input_params: { properties: { "prompt": { type: "string" } }, required: [] } },
  ],
  audio_models: [
    { id: "audio-passthrough", name: "Input Audio", input_params: { properties: { "audio_url": { type: "string" } }, required: [] } },
  ],
  concat_models: [
    { id: "prompt-concatenator", name: "Prompt Concatenator", input_params: { properties: { "prompt": { type: "string" } }, required: [] } },
  ],
  video_combiner_models: [
    { id: "video-combiner", name: "Video Combiner", input_params: { properties: { "videos_list": { type: "array" } }, required: [] } },
  ],
  api_node_models: [
    { id: "grsai", name: "GRSai API", input_params: { properties: {
      "base_url": { type: "string", default: "grsaiapi.com" },
      "api_key": { type: "string" },
      "model": { type: "string", enum: ["gpt-image-2", "gpt-image-2-vip"], default: "gpt-image-2" },
      "prompt": { type: "string" },
      "images": { type: "array", default: [] },
      "aspectRatio": { type: "string", default: "1024x1024" },
      "replyType": { type: "string", enum: ["json", "stream", "async"], default: "json" },
    }, required: ["api_key", "model", "prompt"] } },
  ],
};

async function fetchWorkflowData(id, cookieHeader) {
  const baseUrl = "http://127.0.0.1:8000/api/workflow";
  try {
    const [workflowRes, schemasRes] = await Promise.all([
      fetch(`${baseUrl}/get-workflow-def/${id}`, {
        cache: 'no-store',
        headers: { 'Cookie': cookieHeader || '' }
      }),
      fetch(`${baseUrl}/${id}/node-schemas`, {
        cache: 'no-store',
        headers: { 'Cookie': cookieHeader || '' }
      })
    ]);

    const initialWorkflowData = workflowRes.ok ? await workflowRes.json() : mockWorkflowData;
    const initialNodeSchemas = schemasRes.ok ? await schemasRes.json() : mockNodeSchemas;

    return { initialWorkflowData, initialNodeSchemas };
  } catch (error) {
    console.error("Error fetching workflow data on server:", error);
    return { initialWorkflowData: mockWorkflowData, initialNodeSchemas: mockNodeSchemas };
  }
}

export default async function WorkflowPage({ params }) {
  const { id } = await params;
  const cookieStore = await cookies();
  const cookieHeader = cookieStore.toString();

  const { initialWorkflowData, initialNodeSchemas } = await fetchWorkflowData(id, cookieHeader);

  return (
    <div className="h-dvh w-full bg-black">
      <WorkflowBuilderClient 
        initialWorkflowData={initialWorkflowData} 
        initialNodeSchemas={initialNodeSchemas} 
      />
    </div>
  );
}
