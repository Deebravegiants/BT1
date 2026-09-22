# [M] CVE-2016-2370

## Summary
Severity: Medium
Advisory: CVE-2016-2370
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-06
Source: https://osv.dev/vulnerability/CVE-2016-2370
Type: osv

## Details
A denial of service vulnerability exists in the handling of the MXIT protocol in Pidgin. Specially crafted MXIT data sent from the server could potentially result in an out-of-bounds read. A malicious server or man-in-the-middle attacker can send invalid data to trigger this vulnerability.

## References
- http://www.securityfocus.com/bid/91335
- http://www.talosintelligence.com/reports/TALOS-2016-0138/
- http://www.ubuntu.com/usn/USN-3031-1
- https://security.gentoo.org/glsa/201701-38
- http://www.debian.org/security/2016/dsa-3620
- http://www.pidgin.im/news/security/?id=103
