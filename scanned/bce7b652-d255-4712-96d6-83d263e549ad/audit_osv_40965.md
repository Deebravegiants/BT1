# [M] Capgo - Rate Limit Bypass via User-Controlled device_id Parameter

## Summary
Severity: Medium
Advisory: CVE-2026-56324
Aliases: GHSA-77p2-9rcr-5w27
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-22
Source: https://osv.dev/vulnerability/CVE-2026-56324
Type: osv

## Details
Capgo before 12.128.2 contains a rate limit bypass vulnerability in the channel_self endpoint that allows attackers to circumvent rate limiting by rotating the user-controlled device_id parameter. Attackers can send multiple requests per second by changing device_id values to flood the channel_devices table and cause database exhaustion.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56324.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-77p2-9rcr-5w27
- https://nvd.nist.gov/vuln/detail/CVE-2026-56324
- https://www.vulncheck.com/advisories/capgo-rate-limit-bypass-via-user-controlled-device-id-parameter
