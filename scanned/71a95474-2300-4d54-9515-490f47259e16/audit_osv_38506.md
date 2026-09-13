# [C] FastGPT: NoSQL Injection in loginByPassword leads to Authentication Bypass

## Summary
Severity: Critical
Advisory: CVE-2026-40351
Aliases: GHSA-x8mx-2mr7-h9xg
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-40351
Type: osv

## Details
FastGPT is an AI Agent building platform. In versions prior to 4.14.9.5, the password-based login endpoint uses TypeScript type assertion without runtime validation, allowing an unauthenticated attacker to pass a MongoDB query operator object (e.g., {"$ne": ""}) as the password field. This NoSQL injection bypasses the password check, enabling login as any user including the root administrator. This issue has been fixed in version 4.14.9.5.

## References
- https://github.com/labring/FastGPT/releases/tag/v4.14.9.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40351.json
- https://github.com/labring/FastGPT/security/advisories/GHSA-x8mx-2mr7-h9xg
- https://nvd.nist.gov/vuln/detail/CVE-2026-40351
- https://github.com/labring/FastGPT/commit/bd966d479fbe414d02679cf79f9eaaab3d100a2d
