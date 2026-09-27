# [H] FreeScout Vulnerable to Deserialization of Untrusted Data

## Summary
Severity: High
Advisory: CVE-2025-48389
Aliases: GHSA-jmpv-8q3h-2m8v
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2025-05-29
Source: https://osv.dev/vulnerability/CVE-2025-48389
Type: osv

## Details
FreeScout is a free self-hosted help desk and shared mailbox. Prior to version 1.8.178, FreeScout is vulnerable to deserialization of untrusted data due to insufficient validation. Through the set function, a string with a serialized object can be passed, and when getting an option through the get method, deserialization will occur, which will allow arbitrary code execution This issue has been patched in version 1.8.178.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48389.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-jmpv-8q3h-2m8v
- https://nvd.nist.gov/vuln/detail/CVE-2025-48389
- https://github.com/freescout-help-desk/freescout/commit/f7548a7076a0b6e109001069d6be223fbd96c61e
