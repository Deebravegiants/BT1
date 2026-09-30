# [H] Open WebUI: Non-admin users can delete admin-owned external knowledge connections via knowledge base deletion

## Summary
Severity: High
Advisory: CVE-2026-87998
Aliases: GHSA-2724-6cpj-gf3v
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-87998
Type: osv

## Details
Open WebUI is an extensible, feature-rich, and user-friendly self-hosted AI platform. From 0.10.0 until 0.11.1, DELETE /api/v1/knowledge/{id}/delete in backend/open_webui/routers/knowledge.py authorized deletion against the knowledge base but then removed its administrator-owned external connection without a separate administrator check or a check for other dependent knowledge bases. A non-administrator with write access to one external knowledge base could delete shared instance configuration and make every other knowledge base using that connection unavailable. This issue is fixed in version 0.11.1.

## References
- https://github.com/open-webui/open-webui/releases/tag/v0.11.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87998.json
- https://github.com/open-webui/open-webui/security/advisories/GHSA-2724-6cpj-gf3v
- https://nvd.nist.gov/vuln/detail/CVE-2026-87998
- https://github.com/open-webui/open-webui/commit/dc03e7e595d61be97b25a1dd7bb99ad264f73199
- https://github.com/open-webui/open-webui/pull/28113
