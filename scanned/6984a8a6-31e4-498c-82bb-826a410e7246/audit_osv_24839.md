# [M] CVE-2023-27536

## Summary
Severity: Medium
Advisory: CVE-2023-27536
Aliases: CURL-CVE-2023-27536
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-03-30
Source: https://osv.dev/vulnerability/CVE-2023-27536
Type: osv

## Details
An authentication bypass vulnerability exists libcurl <8.0.0 in the connection reuse feature which can reuse previously established connections with incorrect user permissions due to a failure to check for changes in the CURLOPT_GSSAPI_DELEGATION option. This vulnerability affects krb5/kerberos/negotiate/GSSAPI transfers and could potentially result in unauthorized access to sensitive information. The safest option is to not reuse connections if the CURLOPT_GSSAPI_DELEGATION option has been changed.

## References
- https://hackerone.com/reports/1895135
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/27xxx/CVE-2023-27536.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/36NBD5YLJXXEDZLDGNFCERWRYJQ6LAQW/
- https://nvd.nist.gov/vuln/detail/CVE-2023-27536
- https://security.gentoo.org/glsa/202310-12
- https://security.netapp.com/advisory/ntap-20230420-0010/
- https://lists.debian.org/debian-lts-announce/2023/04/msg00025.html
