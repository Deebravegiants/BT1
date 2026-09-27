# [M] CVE-2016-9435

## Summary
Severity: Medium
Advisory: CVE-2016-9435
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-01-20
Source: https://osv.dev/vulnerability/CVE-2016-9435
Type: osv

## Details
The HTMLtagproc1 function in file.c in w3m before 0.5.3+git20161009 does not properly initialize values, which allows remote attackers to crash the application via a crafted html file, related to <dd> tags.

## References
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00084.html
- http://www.securityfocus.com/bid/94407
- https://security.gentoo.org/glsa/201701-08
- http://www.openwall.com/lists/oss-security/2016/11/18/3
- https://github.com/tats/w3m/commit/33509cc81ec5f2ba44eb6fd98bd5c1b5873e46bd
- https://github.com/tats/w3m/issues/16
