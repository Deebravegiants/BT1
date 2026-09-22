# [H] Capgo - SSRF and Privilege Escalation via Path Traversal in Builder Upload Proxy

## Summary
Severity: High
Advisory: CVE-2026-56233
Aliases: GHSA-qprp-873h-mx6f
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-56233
Type: osv

## Details
Capgo before 12.128.2 contains a path traversal vulnerability in the builder upload proxy that allows authenticated users with build permissions to bypass upload restrictions. Attackers can append traversal sequences to the upload path, which are normalized by the WHATWG URL parser, enabling access to internal administrative endpoints with the privileged BUILDER_API_KEY header and resulting in server-side privilege escalation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56233.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-qprp-873h-mx6f
- https://nvd.nist.gov/vuln/detail/CVE-2026-56233
- https://www.vulncheck.com/advisories/capgo-ssrf-and-privilege-escalation-via-path-traversal-in-builder-upload-proxy
