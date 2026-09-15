# [H] CVE-2019-20838

## Summary
Severity: High
Advisory: CVE-2019-20838
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-15
Source: https://osv.dev/vulnerability/CVE-2019-20838
Type: osv

## Details
libpcre in PCRE before 8.43 allows a subject buffer over-read in JIT when UTF is disabled, and \X or \R has more than one fixed quantifier, a related issue to CVE-2019-20454.

## References
- http://seclists.org/fulldisclosure/2020/Dec/32
- http://seclists.org/fulldisclosure/2021/Feb/14
- https://lists.apache.org/thread.html/rf9fa47ab66495c78bb4120b0754dd9531ca2ff0430f6685ac9b07772%40%3Cdev.mina.apache.org%3E
- https://support.apple.com/kb/HT211931
- https://support.apple.com/kb/HT212147
- https://www.pcre.org/original/changelog.txt
- https://bugs.gentoo.org/717920
