# [H] CVE-2017-2870

## Summary
Severity: High
Advisory: CVE-2017-2870
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-05
Source: https://osv.dev/vulnerability/CVE-2017-2870
Type: osv

## Details
An exploitable integer overflow vulnerability exists in the tiff_image_parse functionality of Gdk-Pixbuf 2.36.6 when compiled with Clang. A specially crafted tiff file can cause a heap-overflow resulting in remote code execution. An attacker can send a file or a URL to trigger this vulnerability.

## References
- http://www.securityfocus.com/bid/100541
- https://lists.debian.org/debian-lts-announce/2019/12/msg00025.html
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2017-0377
