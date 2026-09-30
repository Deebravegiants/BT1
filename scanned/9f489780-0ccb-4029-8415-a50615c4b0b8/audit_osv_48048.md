# [H] CVE-2017-17530

## Summary
Severity: High
Advisory: CVE-2017-17530
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-14
Source: https://osv.dev/vulnerability/CVE-2017-17530
Type: osv

## Details
common/help.c in Geomview 1.9.5 does not validate strings before launching the program specified by the BROWSER environment variable, which might allow remote attackers to conduct argument-injection attacks via a crafted URL. NOTE: this is disputed by a third party because no untrusted input can be used for the injection

## References
- https://bugs.gentoo.org/650894#c2
- https://security-tracker.debian.org/tracker/CVE-2017-17530
