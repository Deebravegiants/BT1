# [M] CVE-2023-28484

## Summary
Severity: Medium
Advisory: CVE-2023-28484
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-04-24
Source: https://osv.dev/vulnerability/CVE-2023-28484
Type: osv

## Details
In libxml2 before 2.10.4, parsing of certain invalid XSD schemas can lead to a NULL pointer dereference and subsequently a segfault. This occurs in xmlSchemaFixupComplexType in xmlschemas.c.

## References
- https://gitlab.gnome.org/GNOME/libxml2/-/releases/v2.10.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28484.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-28484
- https://security.netapp.com/advisory/ntap-20230601-0006/
- https://security.netapp.com/advisory/ntap-20240201-0005/
- https://gitlab.gnome.org/GNOME/libxml2/-/issues/491
- https://lists.debian.org/debian-lts-announce/2023/04/msg00031.html
