# [C] CVE-2023-23914

## Summary
Severity: Critical
Advisory: CVE-2023-23914
Aliases: CURL-CVE-2023-23914
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2023-02-23
Source: https://osv.dev/vulnerability/CVE-2023-23914
Type: osv

## Details
A cleartext transmission of sensitive information vulnerability exists in curl <v7.88.0 that could cause HSTS functionality fail when multiple URLs are requested serially. Using its HSTS support, curl can be instructed to use HTTPS instead of usingan insecure clear-text HTTP step even when HTTP is provided in the URL. ThisHSTS mechanism would however surprisingly be ignored by subsequent transferswhen done on the same command line because the state would not be properlycarried on.

## References
- https://hackerone.com/reports/1813864
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/23xxx/CVE-2023-23914.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-23914
- https://security.gentoo.org/glsa/202310-12
- https://security.netapp.com/advisory/ntap-20230309-0006/
