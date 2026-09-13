# [C] FreeRDP - Heap-buffer-overflow in gdi_CacheToSurface via rectangle validation bypass

## Summary
Severity: Critical
Advisory: CVE-2026-40033
Aliases: CVE-2026-44421, GHSA-p6r2-4hgm-m6ff
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-40033
Type: osv

## Details
FreeRDP before 3.26.0 contains a heap-buffer-overflow vulnerability in gdi_CacheToSurface that allows remote attackers to write out-of-bounds heap memory. The vulnerability occurs because rectangle validation clamps coordinates to UINT16_MAX but performs copy operations using unclamped cache entry dimensions, enabling malicious RDP servers to trigger large out-of-bounds writes and potentially achieve remote code execution or client crash.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-40033.json
- https://access.redhat.com/errata/RHSA-2026:36203
- https://access.redhat.com/errata/RHSA-2026:46393
- https://access.redhat.com/security/cve/CVE-2026-40033
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40033.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-p6r2-4hgm-m6ff
- https://nvd.nist.gov/vuln/detail/CVE-2026-40033
- https://www.vulncheck.com/advisories/freerdp-heap-buffer-overflow-in-gdi-cachetosurface-via-rectangle-validation-bypass
- https://bugzilla.redhat.com/show_bug.cgi?id=2481473
- https://github.com/FreeRDP/FreeRDP/pull/12713
- https://github.com/FreeRDP/FreeRDP/commit/d7508ebcd82842a691ae4941e5104d14240a89ae
