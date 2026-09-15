# [H] External Control of File Name or Path in Langflow

## Summary
Severity: High
Advisory: GHSA-f43r-cc68-gpx4
CVE: CVE-2025-68478
CWE: CWE-610, CWE-73
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2025-12-19
Source: https://github.com/advisories/GHSA-f43r-cc68-gpx4
Type: github-advisory

## Affected
- PyPI: `langflow` — affected >=0 <1.7.1

## Details
**Vulnerability Overview**

If an arbitrary path is specified in the request body's `fs_path`, the server serializes the Flow object into JSON and creates/overwrites a file at that path. There is no path restriction, normalization, or allowed directory enforcement, so absolute paths (e.g., /etc/poc.txt) are interpreted as is.

**Vulnerable Code**

1. It receives the request body (flow), updates the DB, and then passes it to the file-writing sink.
    
    https://github.com/langflow-ai/langflow/blob/ac6e2d2eabeee28085f2739d79f7ce4205ca082c/src/backend/base/langflow/api/v1/flows.py#L154-L168
    
    ```python
    @router.post("/", response_model=FlowRead, status_code=201)
    async def create_flow(
        *,
        session: DbSession,
        flow: FlowCreate,
        current_user: CurrentActiveUser,
    ):
        try:
            db_flow = await _new_flow(session=session, flow=flow, user_id=current_user.id)
            await session.commit()
            await session.refresh(db_flow)
    
            await _save_flow_to_fs(db_flow)
    
        except Exception as e:
    ```
    
2. Applies authentication dependency (requires API Key/JWT) when accessing the endpoint.
    
    https://github.com/langflow-ai/langflow/blob/ac6e2d2eabeee28085f2739d79f7ce4205ca082c/src/backend/base/langflow/api/utils/core.py#L36-L38
    
    ```python
    CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]
    CurrentActiveMCPUser = Annotated[User, Depends(get_current_active_user_mcp)]
    DbSession = Annotated[AsyncSession, Depends(get_session)]
    ```
    
3. The client can directly specify the save path, including `fs_path`.
    
    https://github.com/langflow-ai/langflow/blob/ac6e2d2eabeee28085f2739d79f7ce4205ca082c/src/backend/base/langflow/api/v1/flows.py#L66-L70
    
    ```python
    ):
        try:
            await _verify_fs_path(flow.fs_path)
    
            """Create a new flow."""
    ```
    
4. It attempts to create the file (or *the* file, in the case of a path without a parent) directly without path validation.
    
    https://github.com/langflow-ai/langflow/blob/ac6e2d2eabeee28085f2739d79f7ce4205ca082c/src/backend/base/langflow/api/v1/flows.py#L45-L49
    
    ```python
    async def _verify_fs_path(path: str | None) -> None:
        if path:
            path_ = Path(path)
            if not await path_.exists():
                await path_.touch()
    ```
    
5. Serializes the Flow object to JSON and writes it to the specified path in "w" mode (overwriting).
    
    https://github.com/langflow-ai/langflow/blob/ac6e2d2eabeee28085f2739d79f7ce4205ca082c/src/backend/base/langflow/api/v1/flows.py#L52-L58
    
    ```python
    async def _save_flow_to_fs(flow: Flow) -> None:
        if flow.fs_path:
            async with async_open(flow.fs_path, "w") as f:
                try:
                    await f.write(flow.model_dump_json())
                except OSError:
                    await logger.aexception("Failed to write flow %s to path %s", flow.name, flow.fs_path)
    ```
    

**PoC Description**

When an authenticated user passes an arbitrary path in `fs_path`, the Flow JSON is written to that path. Since `/tmp` is usually writable, it is easy to reproduce. In a production environment, writing to system-protected directories may fail depending on permissions.

**PoC**

- **Before Exploit**
   

    <img width="1918" height="658" alt="image" src="https://github.com/user-attachments/assets/fe3c2306-091d-4cb0-b4dc-c7fb63c03d8d" />
    
- **After Exploit**
    
    ```bash
    curl -sS -X POST "http://localhost:7860/api/v1/flows/" \
      -H "Content-Type: application/json" \
      -H "x-api-key: sk-8Kyzf9IQ-UEJ_OtSTaJq4eniMT9_JKgZ7__q8PNkoxc" \
      -d '{"name":"poc-etc","data":{"nodes":[],"edges":[]},"fs_path":"/tmp/POC.txt"}'
    ```
    
    <img width="1918" height="742" alt="image" src="https://github.com/user-attachments/assets/cc0b0c96-1c2d-4d56-b558-5ba97e0ec174" />
    

### Impact

- **Authenticated Arbitrary File Write (within server permission scope):** Risk of corrupting configuration/log/task files, disrupting application behavior, and tampering with files read by other components.
- **Both absolute and relative paths are allowed, enabling base directory traversal.** The risk of overwriting system files increases in environments with root privileges or weak mount/permission settings.
- **The file content is limited to Flow JSON,** but the impact is severe if the target file is parsed by a JSON parser or is subject to subsequent processing.
- **In production environments, it is essential to enforce a save root, normalize paths, block symlink traversal, and minimize permissions.**

## References
- https://github.com/langflow-ai/langflow/security/advisories/GHSA-f43r-cc68-gpx4
- https://nvd.nist.gov/vuln/detail/CVE-2025-68478
- https://github.com/langflow-ai/langflow
- https://github.com/pypa/advisory-database/tree/main/vulns/langflow/PYSEC-2025-125.yaml
