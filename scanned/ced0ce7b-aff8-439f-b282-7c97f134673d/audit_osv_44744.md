# [M] Onyx 4.6.6 Custom Tool Secret Header Disclosure via Tool Endpoints

## Summary
Severity: Medium
Advisory: CVE-2026-85700
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85700
Type: osv

## Details
Onyx 4.6.6 fails to properly restrict access to custom tool credentials stored in custom_headers, allowing any authenticated user to read admin-defined API keys. Attackers with basic authentication can call GET /tool/{tool_id} or GET /tool endpoints to retrieve plaintext authorization headers and third-party API credentials, then use them to directly access upstream APIs.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85700.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85700
- https://www.vulncheck.com/advisories/onyx-4.6.6-custom-tool-secret-header-disclosure-via-tool-endpoints
- https://github.com/onyx-dot-app/onyx/issues/13165
- https://github.com/onyx-dot-app/onyx
- https://github.com/onyx-dot-app/onyx/blob/v4.6.6/backend/onyx/server/features/tool/api.py
- https://github.com/onyx-dot-app/onyx/blob/v4.6.6/backend/onyx/server/features/tool/models.py
