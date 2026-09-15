# [C] CVE-2019-6443

## Summary
Severity: Critical
Advisory: CVE-2019-6443
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/CVE-2019-6443
Type: osv

## Details
An issue was discovered in NTPsec before 1.1.3. Because of a bug in ctl_getitem, there is a stack-based buffer over-read in read_sysvars in ntp_control.c in ntpd.

## References
- https://github.com/ntpsec/ntpsec/blob/NTPsec_1_1_3/NEWS
- https://dumpco.re/blog/ntpsec-bugs
- https://dumpco.re/bugs/ntpsec-oobread1
- https://www.exploit-db.com/exploits/46175/
