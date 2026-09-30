# [H] CVE-2017-17523

## Summary
Severity: High
Advisory: CVE-2017-17523
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-11
Source: https://osv.dev/vulnerability/CVE-2017-17523
Type: osv

## Details
lilypond-invoke-editor in LilyPond 2.19.80 does not validate strings before launching the program specified by the BROWSER environment variable, which allows remote attackers to conduct argument-injection attacks via a crafted URL, as demonstrated by a --proxy-pac-file argument.

## References
- https://bugs.debian.org/881767
- https://bugs.debian.org/884136
- https://sourceforge.net/p/testlilyissues/issues/5243/
