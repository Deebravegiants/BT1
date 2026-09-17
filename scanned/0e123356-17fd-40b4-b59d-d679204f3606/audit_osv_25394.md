# [M] Libtiff: memory leak in tiffcrop.c

## Summary
Severity: Medium
Advisory: CVE-2023-3576
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-10-04
Source: https://osv.dev/vulnerability/CVE-2023-3576
Type: osv

## Details
A memory leak flaw was found in Libtiff's tiffcrop utility. This issue occurs when tiffcrop operates on a TIFF image file, allowing an attacker to pass a crafted TIFF image file to tiffcrop utility, which causes this memory leak issue, resulting an application crash, eventually leading to a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2024/03/msg00011.html
- https://access.redhat.com/errata/RHSA-2023:6575
- https://access.redhat.com/security/cve/CVE-2023-3576
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3576.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3576
- https://bugzilla.redhat.com/show_bug.cgi?id=2219340
