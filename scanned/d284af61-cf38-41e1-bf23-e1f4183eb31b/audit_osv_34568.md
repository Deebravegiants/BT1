# [M] Libgepub: integer overflow in libgepub's epub archive handling

## Summary
Severity: Medium
Advisory: CVE-2025-6196
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-06-17
Source: https://osv.dev/vulnerability/CVE-2025-6196
Type: osv

## Details
A flaw was found in libgepub, a library used to read EPUB files. The software mishandles file size calculations when opening specially crafted EPUB files, leading to incorrect memory allocations. This issue causes the application to crash. Known affected usage includes desktop services like Tumbler, which may process malicious files automatically when browsing directories. While no direct remote attack vectors are confirmed, any application using libgepub to parse user-supplied EPUB content could be vulnerable to a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2025-6196
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/6xxx/CVE-2025-6196.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-6196
- https://bugzilla.redhat.com/show_bug.cgi?id=2373117
- https://gitlab.gnome.org/GNOME/libgepub/-/issues/18
- https://gitlab.gnome.org/GNOME/libgepub/
