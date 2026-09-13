# [C] CVE-2017-1000501

## Summary
Severity: Critical
Advisory: CVE-2017-1000501
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-01-03
Source: https://osv.dev/vulnerability/CVE-2017-1000501
Type: osv

## Details
Awstats version 7.6 and earlier is vulnerable to a path traversal flaw in the handling of the "config" and "migrate" parameters resulting in unauthenticated remote code execution.

## References
- http://www.awstats.org/
- https://lists.debian.org/debian-lts-announce/2018/01/msg00012.html
- https://security.gentoo.org/glsa/202007-37
- https://www.debian.org/security/2018/dsa-4092
- https://github.com/eldy/awstats/commit/06c0ab29c1e5059d9e0279c6b64d573d619e1651
- https://github.com/eldy/awstats/commit/cf219843a74c951bf5986f3a7fffa3dcf99c3899
