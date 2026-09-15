# [M] CVE-2017-6504

## Summary
Severity: Medium
Advisory: CVE-2017-6504
CVSS: 6.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2017-03-06
Source: https://osv.dev/vulnerability/CVE-2017-6504
Type: osv

## Details
WebUI in qBittorrent before 3.3.11 did not set the X-Frame-Options header, which could potentially lead to clickjacking.

## References
- https://github.com/qbittorrent/qBittorrent/commit/f5ad04766f4abaa78374ff03704316f8ce04627d
- https://www.qbittorrent.org/news.php
