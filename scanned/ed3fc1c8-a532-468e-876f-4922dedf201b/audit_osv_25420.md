# [M] Segmentation fault in fax3encode in libtiff/tif_fax3.c

## Summary
Severity: Medium
Advisory: CVE-2023-3618
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-07-12
Source: https://osv.dev/vulnerability/CVE-2023-3618
Type: osv

## Details
A flaw was found in libtiff. A specially crafted tiff file can lead to a segmentation fault due to a buffer overflow in the Fax3Encode function in libtiff/tif_fax3.c, resulting in a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2023/07/msg00034.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00019.html
- https://packages.fedoraproject.org/
- https://support.apple.com/kb/HT214036
- https://support.apple.com/kb/HT214037
- https://support.apple.com/kb/HT214038
- https://access.redhat.com/security/cve/CVE-2023-3618
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3618.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3618
- https://security.netapp.com/advisory/ntap-20230824-0012/
- https://bugzilla.redhat.com/show_bug.cgi?id=2215865
