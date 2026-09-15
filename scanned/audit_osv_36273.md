# [M] Gimp: gimp: memory corruption due to integer overflow in ico file handling

## Summary
Severity: Medium
Advisory: CVE-2026-2272
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-2272
Type: osv

## Details
A flaw was found in GIMP. An integer overflow vulnerability exists when processing ICO image files, specifically in the `ico_read_info` and `ico_read_icon` functions. This issue arises because a size calculation for image buffers can wrap around due to a 32-bit integer evaluation, allowing oversized image headers to bypass security checks. A remote attacker could exploit this by providing a specially crafted ICO file, leading to a buffer overflow and memory corruption, which may result in an application level denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2026-2272
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/2xxx/CVE-2026-2272.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-2272
- https://bugzilla.redhat.com/show_bug.cgi?id=2438428
- https://gitlab.gnome.org/GNOME/gimp/-/issues/15617
