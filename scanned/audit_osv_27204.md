# [M] SSRF in infiniflow/ragflow

## Summary
Severity: Medium
Advisory: CVE-2024-12779
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-12779
Type: osv

## Details
A Server-Side Request Forgery (SSRF) vulnerability exists in infiniflow/ragflow version 0.12.0. The vulnerability is present in the `POST /v1/llm/add_llm` and `POST /v1/conversation/tts` endpoints. Attackers can specify an arbitrary URL as the `api_base` when adding an `OPENAITTS` model, and subsequently access the `tts` REST API endpoint to read contents from the specified URL. This can lead to unauthorized access to internal web resources.

## References
- https://huntr.com/bounties/3cc748ba-2afb-4bfe-8553-10eb6d6dd4f0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12779.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12779
