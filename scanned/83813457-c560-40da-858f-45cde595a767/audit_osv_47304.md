# [M] CVE-2016-2372

## Summary
Severity: Medium
Advisory: CVE-2016-2372
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:N/A:H)
Published: 2017-01-06
Source: https://osv.dev/vulnerability/CVE-2016-2372
Type: osv

## Details
An information leak exists in the handling of the MXIT protocol in Pidgin. Specially crafted MXIT data sent via the server could potentially result in an out-of-bounds read. A malicious user, server, or man-in-the-middle attacker can send an invalid size for a file transfer which will trigger an out-of-bounds read vulnerability. This could result in a denial of service or copy data from memory to the file, resulting in an information leak if the file is sent to another user.

## References
- http://www.securityfocus.com/bid/91335
- http://www.talosintelligence.com/reports/TALOS-2016-0140/
- http://www.ubuntu.com/usn/USN-3031-1
- https://security.gentoo.org/glsa/201701-38
- http://www.debian.org/security/2016/dsa-3620
- http://www.pidgin.im/news/security/?id=105
