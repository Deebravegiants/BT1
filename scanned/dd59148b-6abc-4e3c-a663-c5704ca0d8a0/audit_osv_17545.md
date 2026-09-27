# [H] CVE-2020-16158

## Summary
Severity: High
Advisory: CVE-2020-16158
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-10-19
Source: https://osv.dev/vulnerability/CVE-2020-16158
Type: osv

## Details
GoPro gpmf-parser through 1.5 has a stack out-of-bounds write vulnerability in GPMF_ExpandComplexTYPE(). Parsing malicious input can result in a crash or potentially arbitrary code execution.

## References
- https://blog.inhq.net/posts/gopro-gpmf-parser-vuln-1/
- https://github.com/gopro/gpmf-parser/blob/2cc0af7ffee6f12934e2d57750bdf292f62b0a97/GPMF_parser.c#L950-L954
