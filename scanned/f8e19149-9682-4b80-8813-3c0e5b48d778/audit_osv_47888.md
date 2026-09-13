# [M] CVE-2017-14407

## Summary
Severity: Medium
Advisory: CVE-2017-14407
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-13
Source: https://osv.dev/vulnerability/CVE-2017-14407
Type: osv

## Details
A stack-based buffer over-read was discovered in filterYule in gain_analysis.c in MP3Gain version 1.5.2. The vulnerability causes an application crash, which leads to remote denial of service.

## References
- https://blogs.gentoo.org/ago/2017/09/08/mp3gain-stack-based-buffer-overflow-in-filteryule-gain_analysis-c/
