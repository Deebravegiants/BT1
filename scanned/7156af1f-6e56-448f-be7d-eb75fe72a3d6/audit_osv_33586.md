# [H] Sandboxie Arbitrary Kernel Write in SbieDrv.sys API (API_GET_SECURE_PARAM)

## Summary
Severity: High
Advisory: CVE-2025-46715
Aliases: GHSA-67p9-6h73-ff7x
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-22
Source: https://osv.dev/vulnerability/CVE-2025-46715
Type: osv

## Details
Sandboxie is a sandbox-based isolation software for 32-bit and 64-bit Windows NT-based operating systems. Starting in version 1.3.0 and prior to version 1.15.12, Api_GetSecureParam fails to sanitize incoming pointers, and implicitly trusts that the pointer the user has passed in is safe to write to. GetRegValue then writes the contents of the SBIE registry entry selected to this address. An attacker can pass in a kernel pointer and the driver dumps the registry key contents we requested to it. This can be triggered by anyone on the system, including low integrity windows processes. Version 1.15.12 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/46xxx/CVE-2025-46715.json
- https://github.com/sandboxie-plus/Sandboxie/security/advisories/GHSA-67p9-6h73-ff7x
- https://nvd.nist.gov/vuln/detail/CVE-2025-46715
