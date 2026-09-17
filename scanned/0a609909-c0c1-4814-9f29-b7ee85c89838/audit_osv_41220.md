# [H] Gimp: gimp: stack buffer overflow in pnmscanner_gettoken()

## Summary
Severity: High
Advisory: CVE-2026-58380
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-58380
Type: osv

## Details
A flaw was found in GIMP's PNM file format parser. When parsing a specially crafted PNM file, the pnmscanner_gettoken() function writes a null terminator one byte past the end of a stack-allocated buffer due to an off-by-one error in the loop boundary check. This could lead to memory corruption, potentially resulting in denial of service or arbitrary code execution.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2026:40751
- https://access.redhat.com/errata/RHSA-2026:62507
- https://access.redhat.com/security/cve/CVE-2026-58380
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58380.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-58380
- https://bugzilla.redhat.com/show_bug.cgi?id=2496135
- https://gitlab.gnome.org/GNOME/gimp/-/issues/16206
- https://gitlab.gnome.org/GNOME/gimp/-/commit/83699817
