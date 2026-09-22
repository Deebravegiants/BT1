# [M] Heap-use-after-free in gdi_set_bounds

## Summary
Severity: Medium
Advisory: CVE-2026-23884
Aliases: GHSA-cfgj-vc84-f3pp
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-01-19
Source: https://osv.dev/vulnerability/CVE-2026-23884
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to version 3.21.0, offscreen bitmap deletion leaves `gdi->drawing` pointing to freed memory, causing UAF when related update packets arrive. A malicious server can trigger a client‑side use after free, causing a crash (DoS) and potential heap corruption with code‑execution risk depending on allocator behavior and surrounding heap layout. Version 3.21.0 contains a patch for the issue.

## References
- https://github.com/FreeRDP/FreeRDP/blob/3370e30e92a021eb680892dda14d642bc8b8727c/libfreerdp/cache/offscreen.c#L114-L122
- https://github.com/FreeRDP/FreeRDP/blob/3370e30e92a021eb680892dda14d642bc8b8727c/libfreerdp/cache/offscreen.c#L87-L91
- https://github.com/FreeRDP/FreeRDP/releases/tag/3.21.0
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-23884.json
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
- https://access.redhat.com/security/cve/CVE-2026-23884
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23884.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-cfgj-vc84-f3pp
