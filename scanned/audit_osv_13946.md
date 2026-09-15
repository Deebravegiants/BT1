# [M] CVE-2018-5736

## Summary
Severity: Medium
Advisory: CVE-2018-5736
CVSS: 5.3 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/CVE-2018-5736
Type: osv

## Details
An error in zone database reference counting can lead to an assertion failure if a server which is running an affected version of BIND attempts several transfers of a slave zone in quick succession. This defect could be deliberately exercised by an attacker who is permitted to cause a vulnerable server to initiate zone transfers (for example: by sending valid NOTIFY messages), causing the named process to exit after failing the assertion test. Affects BIND 9.12.0 and 9.12.1.

## References
- http://www.securityfocus.com/bid/104386
- http://www.securitytracker.com/id/1040941
- https://kb.isc.org/docs/aa-01602
- https://security.netapp.com/advisory/ntap-20180926-0004/
