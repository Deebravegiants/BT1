# [M] Langflow: Unauthenticated Shareable Playground arbitrary local or S3 file read

## Summary
Severity: Medium
Advisory: GHSA-rcjh-r59h-gq37
CVE: CVE-2026-48520
CWE: CWE-73
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-rcjh-r59h-gq37
Type: github-advisory

## Affected
- PyPI: `langflow` — affected >=0 <1.10.0

## Details
### Summary
The "Shareable Playground" (or "Public Flows" in code) contains a potential arbitrary file-read vulnerability, depending on the exact flow configuration used.

By making a flow public, public execution of the flow is allowed. The execution request can contain a list of files that gets read by Langflow and fed into the LLM.
The files path can be any path supported by the storage - it can be either a local file or *S3 path* if supported by the local configuration

### Details
Shareable Playground feature works by enabling the execution of workflows by unauthenticated users, by accessing a link.
Specifically, it enables the route `/api/v1/build_public_tmp` to execute any public flow, given a public flow ID.
This request contains a `files` field that can contain a list of files. The files get read in `LCModelComponent._get_chat_result` in a call to `to_lc_message`. A detailed stacktrace:
```
...
  File "/Users/ori/Work/research/langchain/langflow/src/backend/base/langflow/api/build.py", line 466, in build_vertices
    vertex_build_response: VertexBuildResponse = await _build_vertex(vertex_id, graph, event_manager)
  File "/Users/ori/Work/research/langchain/langflow/src/backend/base/langflow/api/build.py", line 324, in _build_vertex
    vertex_build_result = await graph.build_vertex(
  File "/Users/ori/Work/research/langchain/langflow/src/lfx/src/lfx/graph/graph/base.py", line 1563, in build_vertex
    await vertex.build(
  File "/Users/ori/Work/research/langchain/langflow/src/lfx/src/lfx/graph/vertex/base.py", line 770, in build
    await step(user_id=user_id, event_manager=event_manager, **kwargs)
  File "/Users/ori/Work/research/langchain/langflow/src/lfx/src/lfx/events/observability/lifecycle_events.py", line 95, in wrapper
    result = await observed_method(self, *args, **kwargs)
  File "/Users/ori/Work/research/langchain/langflow/src/lfx/src/lfx/graph/vertex/base.py", line 411, in _build
    await self._build_results(
  File "/Users/ori/Work/research/langchain/langflow/src/lfx/src/lfx/graph/vertex/base.py", line 640, in _build_results
    result = await initialize.loading.get_instance_results(
  File "/Users/ori/Work/research/langchain/langflow/src/lfx/src/lfx/interface/initialize/loading.py", line 76, in get_instance_results
    return await build_component(params=custom_params, custom_component=custom_component)
  File "/Users/ori/Work/research/langchain/langflow/src/lfx/src/lfx/interface/initialize/loading.py", line 299, in build_component
    build_results, artifacts = await custom_component.build_results()
  File "/Users/ori/Work/research/langchain/langflow/src/lfx/src/lfx/custom/custom_component/component.py", line 1136, in build_results
    return await self._build_with_tracing()
  File "/Users/ori/Work/research/langchain/langflow/src/lfx/src/lfx/custom/custom_component/component.py", line 1118, in _build_with_tracing
    results, artifacts = await self._build_results()
  File "/Users/ori/Work/research/langchain/langflow/src/lfx/src/lfx/custom/custom_component/component.py", line 1163, in _build_results
    result = await self._get_output_result(output)
  File "/Users/ori/Work/research/langchain/langflow/src/lfx/src/lfx/custom/custom_component/component.py", line 1238, in _get_output_result
    result = await method() if inspect.iscoroutinefunction(method) else await asyncio.to_thread(method)
  File "/Users/ori/Work/research/langchain/langflow/src/lfx/src/lfx/base/models/model.py", line 88, in text_response
    result = await self.get_chat_result(
  File "/Users/ori/Work/research/langchain/langflow/src/lfx/src/lfx/base/models/model.py", line 180, in get_chat_result
    return await self._get_chat_result(
  File "/Users/ori/Work/research/langchain/langflow/src/lfx/src/lfx/base/models/model.py", line 232, in _get_chat_result
    messages.append(input_value.to_lc_message(self.name))
  File "/Users/ori/Work/research/langchain/langflow/src/lfx/src/lfx/schema/message.py", line 184, in to_lc_message
    file_contents = self.get_file_content_dicts(model_name)
  File "/Users/ori/Work/research/langchain/langflow/src/lfx/src/lfx/schema/message.py", line 256, in get_file_content_dicts
    content_dicts.append(create_image_content_dict(file, None, model_name))
  File "/Users/ori/Work/research/langchain/langflow/src/lfx/src/lfx/utils/image.py", line 96, in create_image_content_dict
    ...
```

This triggers Langflow to feed the file into the LLM as an Image. Reading the files back depends on the specific LLM configuration.

### PoC
Reproduction:
1. Create a new flow and add a Chat Input node to it
2. Share the flow ("Shareable Playground")
3. Access the public link with the browser developers tools open and execute the flow.
4. Find the `/api/v1/build_public_tmp` route and copy as cURL
5. Edit the `files` JSON field to point to any file.

### Impact
Potential file read (local or S3) if shareable playground feature is used.



Ori Lahav
Security Researcher @ Rubrik Inc.

## References
- https://github.com/langflow-ai/langflow/security/advisories/GHSA-rcjh-r59h-gq37
- https://nvd.nist.gov/vuln/detail/CVE-2026-48520
- https://github.com/langflow-ai/langflow
- https://github.com/pypa/advisory-database/tree/main/vulns/langflow/PYSEC-2026-244.yaml
