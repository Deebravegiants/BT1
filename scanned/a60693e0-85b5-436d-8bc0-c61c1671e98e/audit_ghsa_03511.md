# [H] Out-of-bounds write in libpng

## Summary
Severity: High
Advisory: GHSA-qwwr-qc2p-6283
CVE: CVE-2018-14550
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-03-22
Source: https://github.com/advisories/GHSA-qwwr-qc2p-6283
Type: github-advisory

## Affected
- NuGet: `libpng` — affected >=0 <1.6.37

## Details
An issue has been found in third-party PNM decoding associated with libpng 1.6.35. It is a stack-based buffer overflow in the function get_token in pnm2png.c in pnm2png.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-14550
- https://github.com/glennrp/libpng/issues/246
- https://github.com/fouzhe/security/tree/master/libpng#stack-buffer-overflow-in-png2pnm-in-function-get_token
- https://github.com/glennrp/libpng
- https://security.gentoo.org/glsa/201908-02
- https://security.netapp.com/advisory/ntap-20221028-0001
- https://snyk.io/vuln/SNYK-UPSTREAM-LIBPNG-1043612
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
