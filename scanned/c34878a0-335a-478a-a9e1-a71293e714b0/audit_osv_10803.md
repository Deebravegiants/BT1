# [H] CVE-2017-2862

## Summary
Severity: High
Advisory: CVE-2017-2862
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-05
Source: https://osv.dev/vulnerability/CVE-2017-2862
Type: osv

## Details
An exploitable heap overflow vulnerability exists in the gdk_pixbuf__jpeg_image_load_increment functionality of Gdk-Pixbuf 2.36.6. A specially crafted jpeg file can cause a heap overflow resulting in remote code execution. An attacker can send a file or url to trigger this vulnerability.

## References
- http://www.securityfocus.com/bid/100541
- http://www.debian.org/security/2017/dsa-3978
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2017-0366
