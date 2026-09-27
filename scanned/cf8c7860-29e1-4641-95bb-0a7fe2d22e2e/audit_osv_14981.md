# [C] CVE-2019-12798

## Summary
Severity: Critical
Advisory: CVE-2019-12798
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-13
Source: https://osv.dev/vulnerability/CVE-2019-12798
Type: osv

## Details
An issue was discovered in Artifex MuJS 1.0.5. regcompx in regexp.c does not restrict regular expression program size, leading to an overflow of the parsed syntax list size.

## References
- http://git.ghostscript.com/?p=mujs.git%3Bh=7f50591861525f76e3ec7a63392656ff8c030af9
- http://www.securityfocus.com/bid/108774
