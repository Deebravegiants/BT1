# [H] Open WebUI's process_files_batch() endpoint missing ownership check, allows unauthorized file overwrite

## Summary
Severity: High
Advisory: GHSA-jjp7-g2jw-wh3j
CVE: CVE-2026-28788
CWE: CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-jjp7-g2jw-wh3j
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.8.6

## Details
### Summary

Any authenticated user can overwrite any file's content by ID through the `POST /api/v1/retrieval/process/files/batch` endpoint. The endpoint performs no ownership check, so a regular user with read access to a shared knowledge base can obtain file UUIDs via `GET /api/v1/knowledge/{id}/files` and then overwrite those files, escalating from read to write. The overwritten content is served to the LLM via RAG, meaning the attacker controls what the model tells other users.

### Details

The `process_files_batch()` function in `backend/open_webui/routers/retrieval.py` appears to be designed as an internal helper. The knowledge base router (`add_files_to_knowledge_batch()` in `knowledge.py`) imports and calls it directly after performing its own ownership and access control checks. The frontend never calls the retrieval route directly; all legitimate UI flows go through the knowledge base wrapper.

However, the function is also exposed as a standalone HTTP endpoint via `@router.post(...)`. This direct route only requires `get_verified_user` (any authenticated user) and performs no ownership check of its own:

```python
for file in form_data.files:
    text_content = file.data.get("content", "")  # attacker-controlled

    file_updates.append(FileUpdateForm(
        hash=calculate_sha256_string(text_content),
        data={"content": text_content},            # written to DB
    ))

for file_update, file_result in zip(file_updates, file_results):
    Files.update_file_by_id(id=file_result.file_id, form_data=file_update)
    #                       ^^^ no ownership check
```

There is no verification that `file.user_id == user.id` before the write. Any authenticated user who knows a file UUID can overwrite that file.

**How an attacker obtains file UUIDs:**

Same as with read access, any user who can see a knowledge base can retrieve file IDs for every document in it via `GET /api/v1/knowledge/{id}/files`. In deployments where knowledge bases are shared across teams, this gives any regular user a list of valid targets.

**Suggested fix:** Add an ownership check before writing:

```python
for file in form_data.files:
    db_file = Files.get_file_by_id(file.id)
    if not db_file or (db_file.user_id != user.id and user.role != "admin"):
        file_errors.append(BatchProcessFilesResult(
            file_id=file.id, status="failed",
            error="Permission denied: not file owner",
        ))
        continue
```

**Classification:**
- CWE-639: Authorization Bypass Through User-Controlled Key
- OWASP API1:2023: Broken Object Level Authorization

Tested on Open WebUI **0.8.3** using a default Docker configuration.

### PoC

**Prerequisites:**
- Default Open WebUI installation (Docker: `ghcr.io/open-webui/open-webui:main`)
- An admin or user creates a knowledge base with shared read access and uploads a file
- A regular user account exists (the attacker)

**Obtaining the file UUID (attacker):**

```
GET /api/v1/knowledge/{kb_id}/files
```

This returns metadata for all files in the KB, including their UUIDs.

**Exploit (attacker):**

```bash
python3 poc_exploit.py --url http://<host>:3000 --file-id <target-file-uuid> -t <attacker-jwt>
```

The PoC script: [poc_exploit.py](https://github.com/user-attachments/files/25470374/poc_exploit.py)
1. Authenticates as the attacker
2. Overwrites the target file via `POST /api/v1/retrieval/process/files/batch` with a canary payload containing a unique marker string
3. Reads the file back and confirms the attacker's content replaced the original

**Verifying RAG poisoning:**

After the overwrite, log in as any other user, start a chat with the poisoned knowledge base attached, and ask about the document. The model's response will include the attacker's canary string (`BOLA-<marker>`), confirming that attacker-controlled content reached the LLM and influenced the response.

No special tooling is required. The script uses only Python 3 standard library (`urllib`).

### Impact

**Who is affected:** Any multi-user Open WebUI deployment where knowledge bases are shared. The attacker needs a valid account (any role) and a target file UUID, which is available through any knowledge base they have read access to.

**What can happen:**
- **RAG poisoning:** The overwritten content is served to the LLM via RAG. The attacker controls what the model tells every user who queries that knowledge base. This includes the ability to inject instructions the model will follow, which could lead to further exploitation depending on what tools and capabilities are available in the deployment (e.g. code interpreter, function calling).
- **Silent data corruption:** The original file content is permanently replaced with no indication to the file owner or other users that it has changed.
- **No audit trail:** Nothing records that an unauthorized user modified the file.

The core issue is that a function designed as an internal helper is exposed as a public endpoint without its own authorization checks. A user with read-only access to a knowledge base can escalate to write access over any file in it.

### Disclaimer on the use of AI powered tools

The research and reporting related to this vulnerability was aided by the help of AI tools.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-jjp7-g2jw-wh3j
- https://nvd.nist.gov/vuln/detail/CVE-2026-28788
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.8.6
