# [M] CVE-2019-6445

## Summary
Severity: Medium
Advisory: CVE-2019-6445
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/CVE-2019-6445
Type: osv

## Details
An issue was discovered in NTPsec before 1.1.3. An authenticated attacker can cause a NULL pointer dereference and ntpd crash in ntp_control.c, related to ctl_getitem.

## References
- https://github.com/ntpsec/ntpsec/blob/NTPsec_1_1_3/NEWS
- https://dumpco.re/blog/ntpsec-bugs
- https://dumpco.re/bugs/ntpsec-authed-npe
- https://www.exploit-db.com/exploits/46177/
