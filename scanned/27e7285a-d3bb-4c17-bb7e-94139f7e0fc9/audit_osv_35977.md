# [C] libjxl: Out-of-bounds write in grayscale color transformation when using LCMS2

## Summary
Severity: Critical
Advisory: CVE-2026-1837
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-11
Source: https://osv.dev/vulnerability/CVE-2026-1837
Type: osv

## Details
A specially-crafted file can cause libjxl's decoder to write pixel data to uninitialized unallocated memory. Soon after that data from another uninitialized unallocated region is copied to pixel data.

This can be done by requesting color transformation of grayscale images to another grayscale color space. Buffers allocated for 1-float-per-pixel are used as if they are allocated for 3-float-per-pixel. That happens only if LCMS2 is used as CMS engine. There is another CMS engine available (selected by build flags).

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-1837.json
- https://access.redhat.com/security/cve/CVE-2026-1837
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/1xxx/CVE-2026-1837.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-1837
- https://bugzilla.redhat.com/show_bug.cgi?id=2438974
- https://github.com/libjxl/libjxl/issues/4549
