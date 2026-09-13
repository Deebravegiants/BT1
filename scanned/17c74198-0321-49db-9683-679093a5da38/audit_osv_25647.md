# [M] Libtiff: integer overflow in tiffcp.c

## Summary
Severity: Medium
Advisory: CVE-2023-40745
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-10-05
Source: https://osv.dev/vulnerability/CVE-2023-40745
Type: osv

## Details
LibTIFF is vulnerable to an integer overflow. This flaw allows remote attackers to cause a denial of service (application crash) or possibly execute an arbitrary code via a crafted tiff image, which triggers a heap-based buffer overflow.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2024:2289
- https://access.redhat.com/security/cve/CVE-2023-40745
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/40xxx/CVE-2023-40745.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-40745
- https://security.netapp.com/advisory/ntap-20231110-0005/
- https://bugzilla.redhat.com/show_bug.cgi?id=2235265
- https://gitlab.com/libtiff/libtiff
