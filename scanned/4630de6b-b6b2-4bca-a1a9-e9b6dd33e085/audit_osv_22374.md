# [H] CVE-2022-27775

## Summary
Severity: High
Advisory: CVE-2022-27775
Aliases: CURL-CVE-2022-27775
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-06-01
Source: https://osv.dev/vulnerability/CVE-2022-27775
Type: osv

## Details
An information disclosure vulnerability exists in curl 7.65.0 to 7.82.0 are vulnerable that by using an IPv6 address that was in the connection pool but with a different zone id it could reuse a connection instead.

## References
- https://hackerone.com/reports/1546268
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/27xxx/CVE-2022-27775.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-27775
- https://security.gentoo.org/glsa/202212-01
- https://security.netapp.com/advisory/ntap-20220609-0008/
- https://www.debian.org/security/2022/dsa-5197
