# [M] An authentication bypass vulnerability exists libcurl <8.0.0 in the connection reuse feature which...

## Summary
Severity: Medium
Advisory: JLSEC-2025-30
Ecosystem: Julia
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-10-10
Source: https://osv.dev/vulnerability/JLSEC-2025-30
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.5.0+0
- Julia: `LibCURL_jll` — affected >=0 <8.0.1+0

## Details
An authentication bypass vulnerability exists libcurl <8.0.0 in the connection reuse feature which can reuse previously established connections with incorrect user permissions due to a failure to check for changes in the `CURLOPT_GSSAPI_DELEGATION` option. This vulnerability affects krb5/kerberos/negotiate/GSSAPI transfers and could potentially result in unauthorized access to sensitive information. The safest option is to not reuse connections if the `CURLOPT_GSSAPI_DELEGATION` option has been changed.

## References
- https://hackerone.com/reports/1895135
- https://lists.debian.org/debian-lts-announce/2023/04/msg00025.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/36NBD5YLJXXEDZLDGNFCERWRYJQ6LAQW/
- https://security.gentoo.org/glsa/202310-12
- https://security.netapp.com/advisory/ntap-20230420-0010/
