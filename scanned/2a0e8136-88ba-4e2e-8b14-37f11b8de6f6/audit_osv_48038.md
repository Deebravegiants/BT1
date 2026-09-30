# [H] CVE-2017-17512

## Summary
Severity: High
Advisory: CVE-2017-17512
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-11
Source: https://osv.dev/vulnerability/CVE-2017-17512
Type: osv

## Details
sensible-browser in sensible-utils before 0.0.11 does not validate strings before launching the program specified by the BROWSER environment variable, which allows remote attackers to conduct argument-injection attacks via a crafted URL, as demonstrated by a --proxy-pac-file argument.

## References
- https://lists.debian.org/debian-lts-announce/2017/12/msg00012.html
- https://usn.ubuntu.com/3584-1/
- http://metadata.ftp-master.debian.org/changelogs/main/s/sensible-utils/sensible-utils_0.0.11_changelog
- https://bugs.debian.org/881767
- https://www.debian.org/security/2017/dsa-4071
