# [H] CVE-2019-10064

## Summary
Severity: High
Advisory: CVE-2019-10064
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-02-28
Source: https://osv.dev/vulnerability/CVE-2019-10064
Type: osv

## Details
hostapd before 2.6, in EAP mode, makes calls to the rand() and random() standard library functions without any preceding srand() or srandom() call, which results in inappropriate use of deterministic values. This was fixed in conjunction with CVE-2016-10743.

## References
- http://www.openwall.com/lists/oss-security/2020/02/27/2
- https://lists.debian.org/debian-lts-announce/2020/03/msg00010.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00013.html
- https://w1.fi/cgit/hostap/commit/?id=98a516eae8260e6fd5c48ddecf8d006285da7389
- http://packetstormsecurity.com/files/156573/Hostapd-Insufficient-Entropy.html
- http://seclists.org/fulldisclosure/2020/Feb/26
- http://www.openwall.com/lists/oss-security/2020/02/27/1
