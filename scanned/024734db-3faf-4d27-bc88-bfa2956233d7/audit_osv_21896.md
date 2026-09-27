# [M] LibTIFF tiff2ps resource consumption

## Summary
Severity: Medium
Advisory: CVE-2022-1210
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2022-04-03
Source: https://osv.dev/vulnerability/CVE-2022-1210
Type: osv

## Details
A vulnerability classified as problematic was found in LibTIFF 4.3.0. Affected by this vulnerability is the TIFF File Handler of tiff2ps. Opening a malicious file leads to a denial of service. The attack can be launched remotely but requires user interaction. The exploit has been disclosed to the public and may be used.

## References
- https://gitlab.com/libtiff/libtiff/uploads/c3da94e53cf1e1e8e6d4d3780dc8c42f/example.tiff
- https://vuldb.com/?id.196363
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1210.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-1210
- https://security.gentoo.org/glsa/202210-10
- https://security.netapp.com/advisory/ntap-20220513-0005/
- https://gitlab.com/libtiff/libtiff/-/issues/402
