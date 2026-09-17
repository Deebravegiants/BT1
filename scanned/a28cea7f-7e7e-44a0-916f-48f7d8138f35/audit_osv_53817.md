# [M] CVE-2023-26555

## Summary
Severity: Medium
Advisory: CVE-2023-26555
CVSS: 6.4 (CVSS:3.1/AV:P/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-11
Source: https://osv.dev/vulnerability/CVE-2023-26555
Type: osv

## Details
praecis_parse in ntpd/refclock_palisade.c in NTP 4.2.8p15 has an out-of-bounds write. Any attack method would be complex, e.g., with a manipulated GPS receiver.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IY2SVYH4MKPAXEYHCCXD3Z6VGINLSVHK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Y3VHEHHWCTYSB7HVJLYPVK4RPJZ5LX52/
- https://github.com/spwpun/ntp-4.2.8p15-cves/blob/main/CVE-2023-26555
- https://github.com/spwpun/ntp-4.2.8p15-cves/issues/1#issuecomment-1506546409
