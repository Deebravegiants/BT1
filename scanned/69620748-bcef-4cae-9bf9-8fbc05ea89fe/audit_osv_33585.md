# [H] Sandboxie has Pool Buffer Overflow in SbieDrv.sys API (API_SET_SECURE_PARAM)

## Summary
Severity: High
Advisory: CVE-2025-46713
Aliases: GHSA-5g85-6p6v-r479
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-22
Source: https://osv.dev/vulnerability/CVE-2025-46713
Type: osv

## Details
Sandboxie is a sandbox-based isolation software for 32-bit and 64-bit Windows NT-based operating systems. Starting in version 0.0.1 and prior to 1.15.12, API_SET_SECURE_PARAM may have an arithmetic overflow deep in the memory allocation subsystem that would lead to a smaller allocation than requested, and a buffer overflow. Version 1.15.12 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/46xxx/CVE-2025-46713.json
- https://github.com/sandboxie-plus/Sandboxie/security/advisories/GHSA-5g85-6p6v-r479
- https://nvd.nist.gov/vuln/detail/CVE-2025-46713
