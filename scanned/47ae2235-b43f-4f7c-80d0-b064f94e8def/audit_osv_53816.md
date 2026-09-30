# [M] CVE-2023-26554

## Summary
Severity: Medium
Advisory: CVE-2023-26554
CVSS: 5.6 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-04-11
Source: https://osv.dev/vulnerability/CVE-2023-26554
Type: osv

## Details
mstolfp in libntp/mstolfp.c in NTP 4.2.8p15 has an out-of-bounds write when adding a '\0' character. An adversary may be able to attack a client ntpq process, but cannot attack ntpd.

## References
- https://github.com/spwpun/ntp-4.2.8p15-cves/blob/main/CVE-2023-26554
- https://github.com/spwpun/ntp-4.2.8p15-cves/issues/1#issuecomment-1506667321
