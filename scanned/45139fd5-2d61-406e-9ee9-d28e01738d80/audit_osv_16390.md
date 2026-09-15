# [M] CVE-2019-6442

## Summary
Severity: Medium
Advisory: CVE-2019-6442
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/CVE-2019-6442
Type: osv

## Details
An issue was discovered in NTPsec before 1.1.3. An authenticated attacker can write one byte out of bounds in ntpd via a malformed config request, related to config_remotely in ntp_config.c, yyparse in ntp_parser.tab.c, and yyerror in ntp_parser.y.

## References
- https://github.com/ntpsec/ntpsec/blob/NTPsec_1_1_3/NEWS
- https://dumpco.re/blog/ntpsec-bugs
- https://dumpco.re/bugs/ntpsec-authed-oobwrite
- https://www.exploit-db.com/exploits/46178/
