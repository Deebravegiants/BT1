# [M] Libtiff: potential integer overflow in raw2tiff.c

## Summary
Severity: Medium
Advisory: CVE-2023-41175
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-10-05
Source: https://osv.dev/vulnerability/CVE-2023-41175
Type: osv

## Details
A vulnerability was found in libtiff due to multiple potential integer overflows in raw2tiff.c. This flaw allows remote attackers to cause a denial of service or possibly execute an arbitrary code via a crafted tiff image, which triggers a heap-based buffer overflow.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2024:2289
- https://access.redhat.com/security/cve/CVE-2023-41175
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/41xxx/CVE-2023-41175.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-41175
- https://bugzilla.redhat.com/show_bug.cgi?id=2235264
- https://gitlab.com/libtiff/libtiff
