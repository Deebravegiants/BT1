# [H] CVE-2018-9862

## Summary
Severity: High
Advisory: CVE-2018-9862
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-09
Source: https://osv.dev/vulnerability/CVE-2018-9862
Type: osv

## Details
util.c in runV 1.0.0 for Docker mishandles a numeric username, which allows attackers to obtain root access by leveraging the presence of an initial numeric value on an /etc/passwd line, and then issuing a "docker exec" command with that value in the -u argument, a similar issue to CVE-2016-3697.

## References
- http://www.securityfocus.com/bid/103738
- https://github.com/hyperhq/hyperstart/pull/348
