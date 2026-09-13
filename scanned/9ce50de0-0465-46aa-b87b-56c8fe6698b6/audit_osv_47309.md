# [H] CVE-2016-2377

## Summary
Severity: High
Advisory: CVE-2016-2377
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-06
Source: https://osv.dev/vulnerability/CVE-2016-2377
Type: osv

## Details
A buffer overflow vulnerability exists in the handling of the MXIT protocol in Pidgin. Specially crafted MXIT data sent by the server could potentially result in an out-of-bounds write of one byte. A malicious server can send a negative content-length in response to a HTTP request triggering the vulnerability.

## References
- http://www.debian.org/security/2016/dsa-3620
- http://www.securityfocus.com/bid/91335
- http://www.talosintelligence.com/reports/TALOS-2016-0119/
- http://www.ubuntu.com/usn/USN-3031-1
- https://security.gentoo.org/glsa/201701-38
- http://www.pidgin.im/news/security/?id=93
