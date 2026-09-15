# [H] CVE-2017-3141

## Summary
Severity: High
Advisory: CVE-2017-3141
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/CVE-2017-3141
Type: osv

## Details
The BIND installer on Windows uses an unquoted service path which can enable a local user to achieve privilege escalation if the host file system permissions allow this. Affects BIND 9.2.6-P2->9.2.9, 9.3.2-P1->9.3.6, 9.4.0->9.8.8, 9.9.0->9.9.10, 9.10.0->9.10.5, 9.11.0->9.11.1, 9.9.3-S1->9.9.10-S1, 9.10.5-S1.

## References
- http://www.securityfocus.com/bid/99089
- http://www.securitytracker.com/id/1038693
- https://kb.isc.org/docs/aa-01496
- https://security.gentoo.org/glsa/201708-01
- https://security.netapp.com/advisory/ntap-20180926-0001/
- https://www.exploit-db.com/exploits/42121/
