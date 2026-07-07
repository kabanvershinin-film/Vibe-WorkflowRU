# Анализ существующих эндпоинтов и схем данных

## 1. Сторонние провайдеры и их эндпоинты

### 1.1 Muapi.ai API (основной)
Базовый URL: `https://api.muapi.ai`

| Эндпоинт | Метод | Назначение | Входные данные | Выходные данные |
|----------|-------|------------|----------------|-----------------|
| `/workflow/create` | POST | Создать воркфлоу | `{ ... }` (объект воркфлоу) | `{ "id": "...", "name": "...", ... }` |
| `/workflow/get-workflow-def/{id}` | GET | Получить воркфлоу по ID | ID в URL | `{ "id": "...", "nodes": [...], "edges": [...] }` |
| `/workflow/get-workflow-defs` | GET | Получить все воркфлоу | - | `[ { "id": "...", ... }, ... ]` |
| `/workflow/{workflow_id}/node-schemas` | GET | Получить схемы нод | ID в URL | `{ "image_models": [...], "video_models": [...], ... }` |
| `/workflow/{workflow_id}/api-node-schemas` | GET | Получить схемы API-нод | ID в URL | `{ "api_node_models": [...] }` |
| `/workflow/{workflow_id}/run` | POST | Запустить воркфлоу | `{ ... }` (параметры запуска) | `{ "run_id": "..." }` |
| `/workflow/run/{run_id}/status` | GET | Проверить статус запуска | ID в URL | `{ "nodes": { ... } }` |
| `/workflow/{workflow_id}/node/{node_id}/run` | POST | Запустить один узел | `{ ... }` | `{ "run_id": "..." }` |
| `/workflow/node-run/{node_run_id}` | DELETE | Удалить запуск узла | ID в URL | `{ "status": "ok" }` |
| `/workflow/update-name/{workflow_id}` | POST | Обновить имя воркфлоу | `{ "name": "..." }` | `{ "id": "...", "name": "..." }` |
| `/workflow/update-category/{workflow_id}` | POST | Обновить категорию | `{ "category": "..." }` | `{ ... }` |
| `/workflow/{workflow_id}/publish` | POST | Опубликовать воркфлоу | `{ ... }` | `{ ... }` |
| `/workflow/{workflow_id}/template` | POST | Создать шаблон | `{ ... }` | `{ ... }` |
| `/workflow/cloudfront-signed-url` | POST | Получить подписанную ссылку | `{ "url": "..." }` | `{ "signed_url": "..." }` |
| `/workflow/{workflow_id}/thumbnail` | POST | Сгенерировать превью | `{ ... }` | `{ ... }` |
| `/workflow/get-workflow-last-run/{workflow_id}` | GET | Последний запуск | ID в URL | `{ ... }` |
| `/workflow/architect` | POST | Архитектор воркфлоу | `{ ... }` | `{ "id": "..." }` |
| `/workflow/poll-architect/{id}/result` | GET | Проверить архитектора | ID в URL | `{ ... }` |
| `/app/calculate_dynamic_cost` | POST | Рассчитать стоимость | `{ "task_name": "...", "payload": { ... } }` | `{ "cost": 0.0 }` |
| `/app/get_file_upload_url` | GET | Ссылка для загрузки | Параметры в query | `{ "url": "..." }` |
| `/workflow/{workflow_id}/api-inputs` | GET | API-инпуты | ID в URL | `{ ... }` |
| `/workflow/{workflow_id}/api-execute` | POST | Запустить через API | `{ ... }` | `{ ... }` |
| `/workflow/run/{run_id}/api-outputs` | GET | API-выходы | ID в URL | `{ ... }` |
| `/workflow/delete-workflow-def/{workflow_id}` | DELETE | Удалить воркфлоу | ID в URL | `{ "status": "ok" }` |

Заголовки:
- `Content-Type: application/json`
- `x-api-key: {MU_API_KEY}`

---

### 1.2 GRSai API (дополнительный)
Базовые URL: `https://grsaiapi.com`, `https://grsai.dakka.com.cn`

| Эндпоинт | Метод | Назначение | Входные данные | Выходные данные |
|----------|-------|------------|----------------|-----------------|
| `/v1/api/generate` | POST | Генерация изображения/видео | `{"model":"...", "prompt":"...", "images":[...], "aspectRatio":"...", "replyType":"json"}` | `{"id":"...", "status":"succeeded", "progress":100, "results":[{"url":"..."}]}` |

Заголовки:
- `Content-Type: application/json`
- `Authorization: Bearer {GRSai_API_KEY}`

---

## 2. Список моделей и их ID

### 2.1 Изображения
- `image-passthrough`
- `nano-banana`
- `nano-banana-edit`
- `nano-banana-pro`
- `nano-banana-pro-edit`
- `flux-schnell`
- `flux-2-dev`
- `flux-2-dev-edit`
- `flux-2-flex`
- `flux-2-flex-edit`
- `flux-2-pro`
- `flux-2-pro-edit`
- `bytedance-seedream-v4`
- `bytedance-seedream-edit-v4`
- `bytedance-seedream-v4.5`
- `bytedance-seedream-v4.5-edit`
- `wan2.5-text-to-image`
- `wan2.5-image-edit`
- `wan2.6-text-to-image`
- `wan2.6-image-edit`
- `qwen-image`
- `qwen-image-edit-2511`
- `qwen-image-edit`
- `qwen-image-edit-plus`
- `qwen-image-edit-plus-lora`
- `z-image-turbo`
- `chroma-image`
- `kling-o1-text-to-image`
- `kling-o1-edit-image`
- `grok-imagine-text-to-image`
- `hunyuan-image-2.1`
- `hunyuan-image-3.0`
- `google-imagen4`
- `google-imagen4-fast`
- `google-imagen4-ultra`
- `midjourney-v7-text-to-image`
- `midjourney-v7-image-to-image`
- `midjourney-v7-omni-reference`
- `midjourney-v7-style-reference`
- `vidu-q2-text-to-image`
- `vidu-q2-reference-to-image`

### 2.2 Видео
- `video-passthrough`
- `seedance-lite-t2v`
- `seedance-lite-i2v`
- `seedance-pro-t2v`
- `seedance-pro-i2v`
- `seedance-pro-t2v-fast`
- `seedance-pro-i2v-fast`
- `seedance-v1.5-pro-t2v`
- `seedance-v1.5-pro-i2v`
- `seedance-v1.5-pro-t2v-fast`
- `seedance-v1.5-pro-i2v-fast`
- `seedance-v1.5-pro-video-extend`
- `seedance-v1.5-pro-video-extend-fast`
- `veo3.1-image-to-video`
- `veo3.1-text-to-video`
- `veo3.1-fast-image-to-video`
- `veo3.1-fast-text-to-video`
- `wan2.2-text-to-video`
- `wan2.2-image-to-video`
- `wan2.2-5b-fast-t2v`
- `wan2.2-animate`
- `wan2.2-edit-video`
- `wan2.2-spicy-image-to-video`
- `wan2.2-spicy-video-extend`
- `wan2.5-text-to-video`
- `wan2.5-image-to-video`
- `wan2.5-text-to-video-fast`
- `wan2.5-image-to-video-fast`
- `wan2.6-text-to-video`
- `wan2.6-image-to-video`
- `openai-sora`
- `openai-sora-2-text-to-video`
- `openai-sora-2-image-to-video`
- `openai-sora-2-pro-text-to-video`
- `openai-sora-2-pro-image-to-video`
- `kling-v2.5-turbo-pro-t2v`
- `kling-v2.5-turbo-pro-i2v`
- `kling-v2.5-turbo-std-i2v`
- `kling-v2.6-pro-t2v`
- `kling-v2.6-pro-i2v`
- `kling-v2.6-pro-motion-control`

### 2.3 Текст, Аудио
- `text-passthrough`
- `audio-passthrough`

### 2.4 Утилиты
- `prompt-concatenator`
- `video-combiner`

### 2.5 API-ноды
- `wavespeed`
- `straico`
- `runware`
- `genvr`
- `grsai` (новый)

---
