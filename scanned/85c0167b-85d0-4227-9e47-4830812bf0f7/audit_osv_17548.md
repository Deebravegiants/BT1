# [H] CVE-2020-16161

## Summary
Severity: High
Advisory: CVE-2020-16161
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-10-19
Source: https://osv.dev/vulnerability/CVE-2020-16161
Type: osv

## Details
GoPro gpmf-parser 1.5 has a division-by-zero vulnerability in GPMF_ScaledData(). Parsing malicious input can result in a crash.

## References
- https://blog.inhq.net/posts/gopro-gpmf-parser-vuln-1/
- https://github.com/gopro/gpmf-parser/blob/2cc0af7ffee6f12934e2d57750bdf292f62b0a97/GPMF_parser.c#L1634
- https://github.com/gopro/gpmf-parser/blob/2cc0af7ffee6f12934e2d57750bdf292f62b0a97/GPMF_parser.c#L1653
