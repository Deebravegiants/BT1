# [M] Langflow: Path Traversal in Knowledge Bases API via Creation Endpoint

## Summary
Severity: Medium
Advisory: GHSA-79ph-745m-6wxq
CVE: CVE-2026-42867
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-79ph-745m-6wxq
Type: github-advisory

## Affected
- PyPI: `langflow` — affected >=0 <1.9.0

## Details
## Summary
Langflow is vulnerable to Path Traversal in the Knowledge Bases API (`POST /api/v1/knowledge_bases`). This occurs because user-supplied knowledge base names are used directly to create file paths without proper sanitization or containment checks. An authenticated attacker can exploit this flaw to create directories and write files anywhere on the server's filesystem.

## Details
The vulnerability exists in the `create_knowledge_base` function within `src/backend/base/langflow/api/v1/knowledge_bases.py`. 

This function constructs file paths directly from the user-supplied `name` field without sanitization. The value is concatenated with the user's base directory and passed directly to `kb_path.mkdir()`. Immediately following the directory creation, the application writes `embedding_metadata.json` and `schema.json` into this attacker-controlled path.

## PoC (Proof of Concept)
For the **Create** endpoint, an attacker can supply traversal sequences or absolute paths in the `name` field:

`../victim_user/evil_kb`
or
`/tmp/pwned`

This forces `kb_path.mkdir()` to create directories and write specific application files (`embedding_metadata.json` and `schema.json`) at any reachable path on the server.

## Impact
Any Langflow instance exposing this endpoint to authenticated users is vulnerable. This exposes the server to:
* **Cross-user data compromise:** Creation of directories and files within another tenant's knowledge base space.
* **Arbitrary filesystem manipulation:** Directory creation at any path on the server where the application has write permissions (e.g., `/app/data`).
* **Data overwrite:** Overwriting existing `embedding_metadata.json` and `schema.json` files in attacker-targeted paths, potentially corrupting existing knowledge bases.

## Fixes
The issue was addressed in **PR #12337**. The fix introduces the `_validate_kb_path_containment()` helper function, which uses `Path.is_relative_to()` instead of `startswith()` to enforce strict path boundaries and prevent prefix-ambiguity bugs. This helper is applied before any filesystem operations. Regression tests were added to verify that traversal payloads return a `403 Forbidden`.

## Acknowledgements
Thanks to the security researchers who responsibly disclosed this vulnerability:
* @ddlxstudio
* @nekros1xx

## References
- https://github.com/langflow-ai/langflow/security/advisories/GHSA-79ph-745m-6wxq
- https://nvd.nist.gov/vuln/detail/CVE-2026-42867
- https://github.com/langflow-ai/langflow/pull/12337
- https://github.com/advisories/GHSA-79ph-745m-6wxq
- https://github.com/langflow-ai/langflow
- https://github.com/pypa/advisory-database/tree/main/vulns/langflow/PYSEC-2026-2566.yaml
- https://pypi.org/project/langflow
