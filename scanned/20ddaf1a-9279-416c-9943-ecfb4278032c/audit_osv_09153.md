# [H] CVE-2016-8641

## Summary
Severity: High
Advisory: CVE-2016-8641
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-01
Source: https://osv.dev/vulnerability/CVE-2016-8641
Type: osv

## Details
A privilege escalation vulnerability was found in nagios 4.2.x that occurs in daemon-init.in when creating necessary files and insecurely changing the ownership afterwards. It's possible for the local attacker to create symbolic links before the files are to be created and possibly escalating the privileges with the ownership change.

## References
- http://www.securityfocus.com/bid/95121
- https://security.gentoo.org/glsa/201702-26
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-8641
- https://github.com/NagiosEnterprises/nagioscore/commit/f2ed227673d3b2da643eb5cad26b2d87674f28c1.patch
- https://www.exploit-db.com/exploits/40774/
