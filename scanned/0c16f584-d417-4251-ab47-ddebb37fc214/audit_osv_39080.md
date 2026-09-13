# [M] Libxpm: libxpm: denial of service via out-of-bounds read in xpm file parsing

## Summary
Severity: Medium
Advisory: CVE-2026-4367
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-16
Source: https://osv.dev/vulnerability/CVE-2026-4367
Type: osv

## Details
A flaw was found in libXpm. A local user with low privileges could exploit an Out-of-Bounds Read vulnerability in the `xpmNextWord()` function by processing a specially crafted or very small XPM (X PixMap) image file. This improper validation of file boundaries can cause an internal pointer to read beyond the file's end, leading to application crashes and Denial of Service conditions.

## References
- http://www.openwall.com/lists/oss-security/2026/04/21/3
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://seclists.org/oss-sec/2026/q2/192
- https://access.redhat.com/errata/RHSA-2026:30354
- https://access.redhat.com/errata/RHSA-2026:47072
- https://access.redhat.com/security/cve/CVE-2026-4367
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/4xxx/CVE-2026-4367.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-4367
- https://bugzilla.redhat.com/show_bug.cgi?id=2448984
- https://gitlab.freedesktop.org/xorg/lib/libxpm/-/commit/5448e1bd
