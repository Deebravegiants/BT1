# [H] CVE-2021-33054

## Summary
Severity: High
Advisory: CVE-2021-33054
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-06-04
Source: https://osv.dev/vulnerability/CVE-2021-33054
Type: osv

## Details
SOGo 2.x before 2.4.1 and 3.x through 5.x before 5.1.1 does not validate the signatures of any SAML assertions it receives. Any actor with network access to the deployment could impersonate users when SAML is the authentication method. (Only versions after 2.0.5a are affected.)

## References
- https://www.sogo.nu/news.html
- https://blogs.akamai.com/2021/06/sogo-and-packetfence-impacted-by-saml-implementation-vulnerabilities.html
- https://github.com/inverse-inc/sogo/blob/master/CHANGELOG.md
- https://lists.debian.org/debian-lts-announce/2021/07/msg00007.html
- https://www.debian.org/security/2021/dsa-5029
