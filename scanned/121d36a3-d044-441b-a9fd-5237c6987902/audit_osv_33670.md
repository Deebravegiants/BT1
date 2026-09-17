# [M] FreeScout Has Insufficient Protection Against CRLF-injection

## Summary
Severity: Medium
Advisory: CVE-2025-48388
Aliases: GHSA-c76f-wggm-grcq
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:L/VA:L/SC:N/SI:N/SA:N)
Published: 2025-05-29
Source: https://osv.dev/vulnerability/CVE-2025-48388
Type: osv

## Details
FreeScout is a free self-hosted help desk and shared mailbox. Prior to version 1.8.178, the application performs insufficient validation of user-supplied data, which is used as arguments to string formatting functions. As a result, an attacker can pass a string containing special symbols (\r, \n, \t)to the application. This issue has been patched in version 1.8.178.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48388.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-c76f-wggm-grcq
- https://nvd.nist.gov/vuln/detail/CVE-2025-48388
- https://github.com/freescout-help-desk/freescout/commit/eab97711027fff4bce90ccd2e189cbc184fa0370
