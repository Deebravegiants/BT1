# [M] FreeRDP has heap-buffer-overflow in gdi_SurfaceToSurface

## Summary
Severity: Medium
Advisory: CVE-2026-23532
Aliases: GHSA-fq8c-87hj-7gvr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-01-19
Source: https://osv.dev/vulnerability/CVE-2026-23532
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to version 3.21.0, a client-side heap buffer overflow occurs in the  FreeRDP client’s `gdi_SurfaceToSurface` path due to a mismatch between destination rectangle clamping and the actual copy size. A malicious server can trigger a client‑side heap buffer overflow, causing a crash (DoS) and potential heap corruption with code‑execution risk depending on allocator behavior and surrounding heap layout. Version 3.21.0 contains a patch for the issue.

## References
- https://github.com/FreeRDP/FreeRDP/blob/38514dfa5813aa945a86cfbcec279033f8394468/libfreerdp/gdi/gfx.c#L1368-L1382
- https://github.com/FreeRDP/FreeRDP/releases/tag/3.21.0
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-23532.json
- https://access.redhat.com/errata/RHSA-2026:2048
- https://access.redhat.com/errata/RHSA-2026:2081
- https://access.redhat.com/errata/RHSA-2026:2222
- https://access.redhat.com/errata/RHSA-2026:2714
- https://access.redhat.com/errata/RHSA-2026:2736
- https://access.redhat.com/errata/RHSA-2026:2770
- https://access.redhat.com/errata/RHSA-2026:2824
- https://access.redhat.com/errata/RHSA-2026:2952
- https://access.redhat.com/errata/RHSA-2026:3036
- https://access.redhat.com/errata/RHSA-2026:3037
- https://access.redhat.com/errata/RHSA-2026:3038
- https://access.redhat.com/errata/RHSA-2026:3039
- https://access.redhat.com/errata/RHSA-2026:3041
- https://access.redhat.com/security/cve/CVE-2026-23532
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23532.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-fq8c-87hj-7gvr
- https://nvd.nist.gov/vuln/detail/CVE-2026-23532
