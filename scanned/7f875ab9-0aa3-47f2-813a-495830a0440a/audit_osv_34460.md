# [M] Gimp: gimp integer overflow

## Summary
Severity: Medium
Advisory: CVE-2025-6035
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:H)
Published: 2025-06-13
Source: https://osv.dev/vulnerability/CVE-2025-6035
Type: osv

## Details
A flaw was found in GIMP. An integer overflow vulnerability exists in the GIMP "Despeckle"  plug-in. The issue occurs due to unchecked multiplication of image dimensions, such as width, height, and bytes-per-pixel (img_bpp), which can result in allocating insufficient memory and subsequently performing out-of-bounds writes. This issue could lead to heap corruption, a potential denial of service (DoS), or arbitrary code execution in certain scenarios.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2025/10/msg00022.html
- https://access.redhat.com/security/cve/CVE-2025-6035
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/6xxx/CVE-2025-6035.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-6035
- https://bugzilla.redhat.com/show_bug.cgi?id=2372515
- https://gitlab.gnome.org/GNOME/gimp/-/issues/13518
- https://gitlab.gnome.org/GNOME/gimp/
