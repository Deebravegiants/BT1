# [M] CVE-2023-26553

## Summary
Severity: Medium
Advisory: CVE-2023-26553
CVSS: 5.6 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-04-11
Source: https://osv.dev/vulnerability/CVE-2023-26553
Type: osv

## Details
mstolfp in libntp/mstolfp.c in NTP 4.2.8p15 has an out-of-bounds write when copying the trailing number. An adversary may be able to attack a client ntpq process, but cannot attack ntpd.

## References
- https://github.com/spwpun/ntp-4.2.8p15-cves/blob/main/CVE-2023-26553
- https://github.com/spwpun/ntp-4.2.8p15-cves/issues/1#issuecomment-1506667321
