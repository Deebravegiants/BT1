# [H] FreeRDP has a global-buffer-overflow in crypto_base64_decode

## Summary
Severity: High
Advisory: CVE-2026-22858
Aliases: GHSA-qmqf-m84q-x896
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:P/VC:H/VI:N/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-01-14
Source: https://osv.dev/vulnerability/CVE-2026-22858
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.20.1, global-buffer-overflow was observed in FreeRDP's Base64 decoding path. The root cause appears to be implementation-defined char signedness: on Arm/AArch64 builds, plain char is treated as unsigned, so the guard c <= 0 can be optimized into a simple c != 0 check. As a result, non-ASCII bytes (e.g., 0x80-0xFF) may bypass the intended range restriction and be used as an index into a global lookup table, causing out-of-bounds access. This vulnerability is fixed in 3.20.1.

## References
- https://github.com/FreeRDP/FreeRDP/releases/tag/3.20.1
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-22858.json
- https://access.redhat.com/errata/RHSA-2026:19033
- https://access.redhat.com/errata/RHSA-2026:3067
- https://access.redhat.com/errata/RHSA-2026:3068
- https://access.redhat.com/errata/RHSA-2026:3334
- https://access.redhat.com/errata/RHSA-2026:3975
- https://access.redhat.com/errata/RHSA-2026:4121
- https://access.redhat.com/errata/RHSA-2026:4433
- https://access.redhat.com/errata/RHSA-2026:4437
- https://access.redhat.com/errata/RHSA-2026:4438
- https://access.redhat.com/errata/RHSA-2026:4439
- https://access.redhat.com/errata/RHSA-2026:4440
- https://access.redhat.com/errata/RHSA-2026:4446
- https://access.redhat.com/errata/RHSA-2026:4471
- https://access.redhat.com/errata/RHSA-2026:4489
- https://access.redhat.com/security/cve/CVE-2026-22858
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22858.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-qmqf-m84q-x896
- https://nvd.nist.gov/vuln/detail/CVE-2026-22858
