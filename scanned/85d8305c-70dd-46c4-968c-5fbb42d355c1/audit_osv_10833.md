# [M] CVE-2017-3138

## Summary
Severity: Medium
Advisory: CVE-2017-3138
CVSS: 5.3 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/CVE-2017-3138
Type: osv

## Details
named contains a feature which allows operators to issue commands to a running server by communicating with the server process over a control channel, using a utility program such as rndc. A regression introduced in a recent feature change has created a situation under which some versions of named can be caused to exit with a REQUIRE assertion failure if they are sent a null command string. Affects BIND 9.9.9->9.9.9-P7, 9.9.10b1->9.9.10rc2, 9.10.4->9.10.4-P7, 9.10.5b1->9.10.5rc2, 9.11.0->9.11.0-P4, 9.11.1b1->9.11.1rc2, 9.9.9-S1->9.9.9-S9.

## References
- http://www.securityfocus.com/bid/97657
- http://www.securitytracker.com/id/1038260
- https://kb.isc.org/docs/aa-01471
- https://security.gentoo.org/glsa/201708-01
- https://security.netapp.com/advisory/ntap-20180802-0002/
- https://www.debian.org/security/2017/dsa-3854
