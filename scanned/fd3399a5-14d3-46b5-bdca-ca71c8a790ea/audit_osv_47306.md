# [H] CVE-2016-2374

## Summary
Severity: High
Advisory: CVE-2016-2374
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-06
Source: https://osv.dev/vulnerability/CVE-2016-2374
Type: osv

## Details
An exploitable memory corruption vulnerability exists in the handling of the MXIT protocol in Pidgin. Specially crafted MXIT MultiMX message sent via the server can result in an out-of-bounds write leading to memory disclosure and code execution.

## References
- http://www.securityfocus.com/bid/91335
- http://www.talosintelligence.com/reports/TALOS-2016-0142/
- http://www.ubuntu.com/usn/USN-3031-1
- https://security.gentoo.org/glsa/201701-38
- http://www.debian.org/security/2016/dsa-3620
- http://www.pidgin.im/news/security/?id=107
