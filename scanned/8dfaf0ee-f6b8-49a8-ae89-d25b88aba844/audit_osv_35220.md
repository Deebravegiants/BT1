# [C] RAGFlow has Predictable Token Generation Leading to Authentication Bypass Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2025-69286
Aliases: GHSA-9j5g-g4xm-57w7
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-12-31
Source: https://osv.dev/vulnerability/CVE-2025-69286
Type: osv

## Details
RAGFlow is an open-source RAG (Retrieval-Augmented Generation) engine. In versions prior to 0.22.0, the use of an insecure key generation algorithm in the API key and beta (assistant/agent share auth) token generation process allows these tokens to be mutually derivable. Specifically, both tokens are generated using the same `URLSafeTimedSerializer` with predictable inputs, enabling an unauthorized user who obtains the shared assistant/agent URL to derive the personal API key. This grants them full control over the assistant/agent owner's account. Version 0.22.0 fixes the issue.

## References
- https://github.com/infiniflow/ragflow/blob/v0.20.5/api/apps/system_app.py#L214-L215
- https://github.com/infiniflow/ragflow/blob/v0.20.5/api/utils/__init__.py#L343
- https://github.com/infiniflow/ragflow/blob/v0.20.5/api/utils/api_utils.py#L378
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69286.json
- https://github.com/infiniflow/ragflow/security/advisories/GHSA-9j5g-g4xm-57w7
- https://nvd.nist.gov/vuln/detail/CVE-2025-69286
- https://github.com/infiniflow/ragflow/commit/a3bb4aadcc3494fb27f2a9933b4c46df8eb532e6
