# [C] CVE-2018-10992

## Summary
Severity: Critical
Advisory: CVE-2018-10992
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-11
Source: https://osv.dev/vulnerability/CVE-2018-10992
Type: osv

## Details
lilypond-invoke-editor in LilyPond 2.19.80 does not validate strings before launching the program specified by the BROWSER environment variable, which allows remote attackers to conduct argument-injection attacks via a crafted URL, as demonstrated by a --proxy-pac-file argument, because the GNU Guile code uses the system Scheme procedure instead of the system* Scheme procedure. NOTE: this vulnerability exists because of an incomplete fix for CVE-2017-17523.

## References
- https://bugs.debian.org/898373
