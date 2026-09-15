# [M] Heap-use-after-free in update_pointer_new

## Summary
Severity: Medium
Advisory: CVE-2026-23883
Aliases: GHSA-qcrr-85qx-4p6x
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-01-19
Source: https://osv.dev/vulnerability/CVE-2026-23883
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to version 3.21.0, `xf_Pointer_New` frees `cursorPixels` on failure, then `pointer_free` calls `xf_Pointer_Free` and frees it again, triggering ASan UAF. A malicious server can trigger a client‑side use after free, causing a crash (DoS) and potential heap corruption with code‑execution risk depending on allocator behavior and surrounding heap layout. Version 3.21.0 contains a patch for the issue.

## References
- https://github.com/FreeRDP/FreeRDP/blob/3370e30e92a021eb680892dda14d642bc8b8727c/client/X11/xf_graphics.c#L312-L319
- https://github.com/FreeRDP/FreeRDP/blob/3370e30e92a021eb680892dda14d642bc8b8727c/client/X11/xf_graphics.c#L340
- https://github.com/FreeRDP/FreeRDP/blob/3370e30e92a021eb680892dda14d642bc8b8727c/libfreerdp/cache/pointer.c#L164-L174
- https://github.com/FreeRDP/FreeRDP/releases/tag/3.21.0
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-23883.json
- https://access.redhat.com/errata/RHSA-2026:2048
- https://access.redhat.com/errata/RHSA-2026:2081
- https://access.redhat.com/errata/RHSA-2026:2222
- https://access.redhat.com/errata/RHSA-2026:2736
- https://access.redhat.com/errata/RHSA-2026:2770
- https://access.redhat.com/errata/RHSA-2026:2824
- https://access.redhat.com/errata/RHSA-2026:2952
- https://access.redhat.com/errata/RHSA-2026:3037
- https://access.redhat.com/security/cve/CVE-2026-23883
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23883.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-qcrr-85qx-4p6x
- https://nvd.nist.gov/vuln/detail/CVE-2026-23883
- https://bugzilla.redhat.com/show_bug.cgi?id=2430885
