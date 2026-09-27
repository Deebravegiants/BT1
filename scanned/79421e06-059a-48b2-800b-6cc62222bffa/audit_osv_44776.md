# [M] CVE-2026-86143

## Summary
Severity: Medium
Advisory: CVE-2026-86143
CVSS: 6.9 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-09-05
Source: https://osv.dev/vulnerability/CVE-2026-86143
Type: osv

## Details
In xmlIO in libxml2 before 2.15.4, an inconsistency in xmlOutputWriteCallback and xmlBufUse causes negative lengths to reach write callbacks, aka a lack of a check for integer overflow before calling writecallback. This has security relevance for many types of uses of that length value within a callback.

## References
- https://github.com/GNOME/libxml2/compare/v2.15.3...v2.15.4
- https://gitlab.gnome.org/GNOME/libxml2/-/work_items/1111
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86143.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-86143
- https://github.com/GNOME/libxml2/commit/90f293ba74d28b1d570920382e707586f68ebf35
