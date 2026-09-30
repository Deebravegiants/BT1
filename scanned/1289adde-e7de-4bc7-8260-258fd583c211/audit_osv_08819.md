# [H] CVE-2016-6255

## Summary
Severity: High
Advisory: CVE-2016-6255
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-03-07
Source: https://osv.dev/vulnerability/CVE-2016-6255
Type: osv

## Details
Portable UPnP SDK (aka libupnp) before 1.6.21 allows remote attackers to write to arbitrary files in the webroot via a POST request without a registered handler.

## References
- https://www.exploit-db.com/exploits/40589/
- https://www.tenable.com/security/research/tra-2017-10
- http://www.debian.org/security/2016/dsa-3736
- http://www.securityfocus.com/bid/92050
- https://security.gentoo.org/glsa/201701-52
- https://sourceforge.net/p/pupnp/code/ci/master/tree/ChangeLog
- https://twitter.com/mjg59/status/755062278513319936
- http://www.openwall.com/lists/oss-security/2016/07/18/13
- http://www.openwall.com/lists/oss-security/2016/07/20/5
- https://github.com/mjg59/pupnp-code/commit/be0a01bdb83395d9f3a5ea09c1308a4f1a972cbd
