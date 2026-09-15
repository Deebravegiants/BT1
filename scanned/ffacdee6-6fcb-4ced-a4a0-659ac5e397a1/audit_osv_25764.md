# [H] Libx11: integer overflow in xcreateimage() leading to a heap overflow

## Summary
Severity: High
Advisory: CVE-2023-43787
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-10-10
Source: https://osv.dev/vulnerability/CVE-2023-43787
Type: osv

## Details
A vulnerability was found in libX11 due to an integer overflow within the XCreateImage() function. This flaw allows a local user to trigger an integer overflow and execute arbitrary code with elevated privileges.

## References
- http://www.openwall.com/lists/oss-security/2024/01/24/9
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2023/10/msg00005.html
- https://access.redhat.com/errata/RHSA-2024:2145
- https://access.redhat.com/errata/RHSA-2024:2973
- https://access.redhat.com/security/cve/CVE-2023-43787
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/43xxx/CVE-2023-43787.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-43787
- https://security.netapp.com/advisory/ntap-20231103-0006/
- https://bugzilla.redhat.com/show_bug.cgi?id=2242254
- https://gitlab.freedesktop.org/xorg/lib/libx11
- https://jfrog.com/blog/xorg-libx11-vulns-cve-2023-43786-cve-2023-43787-part-two/
