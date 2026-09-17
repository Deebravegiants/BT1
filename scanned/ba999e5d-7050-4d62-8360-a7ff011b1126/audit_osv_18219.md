# [H] CVE-2020-25097

## Summary
Severity: High
Advisory: CVE-2020-25097
Aliases: GHSA-jvf6-h9gj-pmj6
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2021-03-19
Source: https://osv.dev/vulnerability/CVE-2020-25097
Type: osv

## Details
An issue was discovered in Squid through 4.13 and 5.x through 5.0.4. Due to improper input validation, it allows a trusted client to perform HTTP Request Smuggling and access services otherwise forbidden by the security controls. This occurs for certain uri_whitespace configuration settings.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DJMDRVV677AJL4BZAOLCT5LMFCGBZTC2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FBXFWKIGXPERDVQXG556LLPUOCMQGERC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/O3RYBDMJCPYGOSURWDR3WJTE474UFT77/
- https://security.gentoo.org/glsa/202105-14
- https://security.netapp.com/advisory/ntap-20210727-0010/
- https://www.debian.org/security/2021/dsa-4873
- http://www.squid-cache.org/Versions/v4/changesets/SQUID-2020_11.patch
- http://www.squid-cache.org/Versions/v5/changesets/SQUID-2020_11.patch
- https://github.com/squid-cache/squid/security/advisories/GHSA-jvf6-h9gj-pmj6
