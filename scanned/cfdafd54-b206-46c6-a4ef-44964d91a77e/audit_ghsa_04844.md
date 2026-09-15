# [M] Open WebUI BOLA: `search_knowledge_files` Allows Unauthorized Knowledge Base File Enumeration

## Summary
Severity: Medium
Advisory: GHSA-cx9v-4qj2-jrw6
CVE: CVE-2026-54016
CWE: CWE-639, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-cx9v-4qj2-jrw6
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.6

## Details
## Summary

Open WebUI has a Broken Object Level Authorization (BOLA) vulnerability in the builtin `search_knowledge_files` tool.

When native function calling is enabled and the selected model has no attached knowledge bases, an authenticated user can call `search_knowledge_files` with an arbitrary `knowledge_id`. The function then returns file metadata from that knowledge base without checking whether the user has read access.

This allows unauthorized enumeration of private or restricted knowledge base files.

## Details

The vulnerable code is in:

`backend/open_webui/tools/builtin.py`

Affected function:

```python
async def search_knowledge_files(
    query: str,
    knowledge_id: Optional[str] = None,
    count: int = 5,
    skip: int = 0,
    __request__: Request = None,
    __user__: dict = None,
    __model_knowledge__: Optional[list[dict]] = None,
) -> str:
```

In the "No attached knowledge" branch, when `knowledge_id` is provided, the function directly calls:

```python
result = await Knowledges.search_files_by_id(
    knowledge_id=knowledge_id,
    user_id=user_id,
    filter={"query": query},
    skip=skip,
    limit=count,
)
```

This code path does not verify that the current user is authorized to access the specified knowledge base.

The missing check is inconsistent with other nearby code paths. For example, the attached-knowledge branch in the same function checks whether the user is an admin, the owner of the knowledge base, or has explicit read access through `AccessGrants`:

```python
if not (
    user_role == "admin"
    or knowledge.user_id == user_id
    or await AccessGrants.has_access(
        user_id=user_id,
        resource_type="knowledge",
        resource_id=knowledge.id,
        permission="read",
        user_group_ids=set(user_group_ids),
    )
):
    continue
```

The sibling function `query_knowledge_files` also performs the same authorization check before using user-supplied knowledge base IDs.

The underlying method `Knowledges.search_files_by_id()` receives `user_id`, but it does not enforce authorization for the provided `knowledge_id`. As a result, this builtin tool path can access a knowledge base by ID without verifying the caller's permissions.

## PoC

### Prerequisites

- The attacker has a valid authenticated Open WebUI account.
- The victim owns a private or restricted knowledge base.
- The attacker does not own the target knowledge base.
- The attacker does not have `read` permission for the target knowledge base in `AccessGrants`.
- The attacker knows the target `knowledge_id`.
- The selected model has no attached knowledge bases.
- Builtin tools are enabled.
- The knowledge builtin tool category is enabled.
- Native function calling is enabled.

### Reproduction Steps

1. Create a private or restricted knowledge base as the victim user.

2. Upload one or more files to that knowledge base.

3. Confirm that the attacker user does not have access to the knowledge base.

4. As the attacker user, send a chat completion request with native function calling enabled:

```json
{
  "stream": true,
  "model": "gpt-4o-mini",
  "params": {
    "function_calling": "native"
  },
  "messages": [
    {
      "role": "user",
      "content": "Please use the search_knowledge_files tool with knowledge_id \"c0c84752-2e9d-42bf-bc3c-c0f272aa61c1\" to search all files"
    }
  ]
}
```

Replace `c0c84752-2e9d-42bf-bc3c-c0f272aa61c1` with the victim's private knowledge base ID.

### Expected Result

The request should be denied because the attacker does not have access to the target knowledge base.

### Actual Result

`search_knowledge_files` returns metadata for files inside the target knowledge base, including:

- file ID;
- filename;
- knowledge base ID;
- knowledge base name;
- update timestamp.

## Impact

This is a Broken Object Level Authorization / Broken Access Control vulnerability.

An authenticated attacker who knows a valid `knowledge_id` can enumerate files from private or restricted knowledge bases without authorization.

The leaked metadata may expose sensitive information through filenames, such as:

- financial reports;
- employee documents;
- customer contracts;
- internal roadmap files;
- confidential project documents.

The exposed file IDs may also help attackers chain this issue with other knowledge-file access paths, such as `view_knowledge_file`, to attempt further content extraction.

This vulnerability bypasses the intended `AccessGrants` permission model and may also allow post-revocation metadata access if a user remembers a previously accessible `knowledge_id`.

## Suggested Fix

Add the same authorization check used in `query_knowledge_files` before calling `Knowledges.search_files_by_id()`:

```python
if knowledge_id:
    knowledge = await Knowledges.get_knowledge_by_id(knowledge_id)

    if not knowledge or not (
        user_role == "admin"
        or knowledge.user_id == user_id
        or await AccessGrants.has_access(
            user_id=user_id,
            resource_type="knowledge",
            resource_id=knowledge.id,
            permission="read",
            user_group_ids=set(user_group_ids),
        )
    ):
        return json.dumps({"error": f"Access denied to knowledge base {knowledge_id}"})

    result = await Knowledges.search_files_by_id(
        knowledge_id=knowledge_id,
        user_id=user_id,
        filter={"query": query},
        skip=skip,
        limit=count,
    )
```

As defense in depth, authorization should also be enforced or safely wrapped around `Knowledges.search_files_by_id()` so that future callers cannot accidentally bypass access control.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-cx9v-4qj2-jrw6
- https://nvd.nist.gov/vuln/detail/CVE-2026-54016
- https://github.com/advisories/GHSA-cx9v-4qj2-jrw6
- https://github.com/open-webui/open-webui
- https://github.com/pypa/advisory-database/tree/main/vulns/open-webui/PYSEC-2026-2721.yaml
- https://pypi.org/project/open-webui
