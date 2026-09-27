# [M] Remnawave Backend has a race condition in HWID device limit allows bypassing max devices

## Summary
Severity: Medium
Advisory: CVE-2026-39880
Aliases: GHSA-985p-44h5-v3pq
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:N)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-39880
Type: osv

## Details
Remnawave Backend is the backend for the Remnawave proxy and user management solution. Prior to 2.7.5, a glitch in the HWID device registration logic allows an authenticated user to bypass the configured limit for HWID devices and register more devices than expected, allowing them to resell subscriptions and consume excessive traffic. This vulnerability is fixed in 2.7.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39880.json
- https://github.com/remnawave/backend/security/advisories/GHSA-985p-44h5-v3pq
- https://nvd.nist.gov/vuln/detail/CVE-2026-39880
