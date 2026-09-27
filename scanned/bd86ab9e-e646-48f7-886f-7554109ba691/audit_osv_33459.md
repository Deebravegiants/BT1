# [H] LibreChat RAG API Authentication Bypass

## Summary
Severity: High
Advisory: CVE-2025-41258
CVSS: 8.0 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-18
Source: https://osv.dev/vulnerability/CVE-2025-41258
Type: osv

## Details
LibreChat version 0.8.1-rc2 uses the same JWT secret for the user session mechanism and RAG API which compromises the service-level authentication of the RAG API.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/41xxx/CVE-2025-41258.json
- https://github.com/sbaresearch/advisories/tree/public/2025/SBA-ADV-20251205-01_LibreChat_RAG_API_Authentication_Bypass
- https://nvd.nist.gov/vuln/detail/CVE-2025-41258
- https://github.com/danny-avila/LibreChat
