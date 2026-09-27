# [H] FastGPT: NoSQL Injection in updatePasswordByOld Leads to Account Takeover

## Summary
Severity: High
Advisory: CVE-2026-40352
Aliases: GHSA-422w-vrfj-72g6
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-40352
Type: osv

## Details
FastGPT is an AI Agent building platform. In versions prior to 4.14.9.5, the password change endpoint is vulnerable to NoSQL injection. An authenticated attacker can bypass the "old password" verification by injecting MongoDB query operators. This allows an attacker who has gained a low-privileged session to change the password of their account (or others if combined with ID manipulation) without knowing the current one, leading to full account takeover and persistence. This issue has been fixed in version 4.14.9.5.

## References
- https://github.com/labring/FastGPT/releases/tag/v4.14.9.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40352.json
- https://github.com/labring/FastGPT/security/advisories/GHSA-422w-vrfj-72g6
- https://nvd.nist.gov/vuln/detail/CVE-2026-40352
- https://github.com/labring/FastGPT/commit/bd966d479fbe414d02679cf79f9eaaab3d100a2d
