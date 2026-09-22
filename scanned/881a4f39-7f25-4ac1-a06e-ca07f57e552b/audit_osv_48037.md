# [H] CVE-2017-17511

## Summary
Severity: High
Advisory: CVE-2017-17511
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-14
Source: https://osv.dev/vulnerability/CVE-2017-17511
Type: osv

## Details
KildClient 3.1.0 does not validate strings before launching the program specified by the BROWSER environment variable, which might allow remote attackers to conduct argument-injection attacks via a crafted URL, related to prefs.c and worldgui.c.

## References
- https://lists.debian.org/debian-lts-announce/2017/12/msg00013.html
- https://security-tracker.debian.org/tracker/CVE-2017-17511
