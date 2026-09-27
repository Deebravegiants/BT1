# [H] CVE-2016-2368

## Summary
Severity: High
Advisory: CVE-2016-2368
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-06
Source: https://osv.dev/vulnerability/CVE-2016-2368
Type: osv

## Details
Multiple memory corruption vulnerabilities exist in the handling of the MXIT protocol in Pidgin. Specially crafted MXIT data sent via the server could result in multiple buffer overflows, potentially resulting in code execution or memory disclosure.

## References
- http://www.debian.org/security/2016/dsa-3620
- http://www.securityfocus.com/bid/91335
- http://www.talosintelligence.com/reports/TALOS-2016-0136/
- http://www.ubuntu.com/usn/USN-3031-1
- https://security.gentoo.org/glsa/201701-38
- http://www.pidgin.im/news/security/?id=101
