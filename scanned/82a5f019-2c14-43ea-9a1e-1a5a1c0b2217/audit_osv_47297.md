# [M] CVE-2016-2365

## Summary
Severity: Medium
Advisory: CVE-2016-2365
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-06
Source: https://osv.dev/vulnerability/CVE-2016-2365
Type: osv

## Details
A denial of service vulnerability exists in the handling of the MXIT protocol in Pidgin. Specially crafted MXIT data sent via the server could potentially result in a null pointer dereference. A malicious server or an attacker who intercepts the network traffic can send invalid data to trigger this vulnerability and cause a crash.

## References
- http://www.ubuntu.com/usn/USN-3031-1
- https://security.gentoo.org/glsa/201701-38
- http://www.debian.org/security/2016/dsa-3620
- http://www.securityfocus.com/bid/91335
- http://www.talosintelligence.com/reports/TALOS-2016-0133/
- http://www.pidgin.im/news/security/?id=98
