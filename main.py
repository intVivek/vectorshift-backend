from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import os
from dotenv import load_dotenv

app = FastAPI()

# Allow CORS for all origins
allowed_origin = os.getenv("ALLOWED_ORIGIN", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[allowed_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class Node(BaseModel):
    id: str

class Edge(BaseModel):
    source: str
    target: str

class Pipeline(BaseModel):
    nodes: List[Node]
    edges: List[Edge]

@app.get('/')
def read_root():
    return {'Ping': 'Pong'}

def is_dag(nodes: List[Node], edges: List[Edge]) -> bool:
    graph = {node.id: [] for node in nodes}
    
    for edge in edges:
        graph[edge.source].append(edge.target)
    
    visited = set()
    visiting = set()

    def visit(node_id):
        if node_id in visiting:
            return False  # Cycle detected
        if node_id in visited:
            return True  # Already visited

        visiting.add(node_id)
        for neighbor in graph[node_id]:
            if not visit(neighbor):
                return False
        
        visiting.remove(node_id)
        visited.add(node_id)
        return True

    for node in nodes:
        if not visit(node.id):
            return False
    
    return True

@app.post('/pipelines/parse')
def parse_pipeline(pipeline: Pipeline):
    num_nodes = len(pipeline.nodes)
    num_edges = len(pipeline.edges)
    dag_status = is_dag(pipeline.nodes, pipeline.edges)
    
    return {'num_nodes': num_nodes, 'num_edges': num_edges, 'is_dag': dag_status}
