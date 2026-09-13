# [H] CVE-2018-5702

## Summary
Severity: High
Advisory: CVE-2018-5702
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-01-15
Source: https://osv.dev/vulnerability/CVE-2018-5702
Type: osv

## Details
Transmission through 2.92 relies on X-Transmission-Session-Id (which is not a forbidden header for Fetch) for access control, which allows remote attackers to execute arbitrary RPC commands, and consequently write to arbitrary files, via POST requests to /transmission/rpc in conjunction with a DNS rebinding attack.

## References
- https://lists.debian.org/debian-lts-announce/2018/01/msg00020.html
- https://security.gentoo.org/glsa/201806-07
- https://twitter.com/taviso/status/951526615145566208
- https://www.debian.org/security/2018/dsa-4087
- https://bugs.chromium.org/p/project-zero/issues/detail?id=1447
- https://github.com/transmission/transmission/pull/468
- https://www.exploit-db.com/exploits/43665/
