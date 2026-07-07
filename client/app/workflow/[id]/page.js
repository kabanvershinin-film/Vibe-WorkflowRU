import React from 'react';
import { cookies } from "next/headers";
import WorkflowBuilderClient from "./WorkflowBuilderClient";

// Моковые данные для демо-режима
const mockWorkflowData = {
  id: "demo",
  name: "Demo Workflow",
  nodes: [],
  edges: [],
  data: { nodes: [] }
};

// Моковые схемы нод
const mockNodeSchemas = {
  image_models: [],
  video_models: [],
  text_models: [],
  audio_models: [],
  concat_models: [],
  video_combiner_models: [],
  api_node_models: [],
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
