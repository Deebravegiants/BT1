# [M] CVE-2016-9317

## Summary
Severity: Medium
Advisory: CVE-2016-9317
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-01-26
Source: https://osv.dev/vulnerability/CVE-2016-9317
Type: osv

## Details
The gdImageCreate function in the GD Graphics Library (aka libgd) before 2.2.4 allows remote attackers to cause a denial of service (system hang) via an oversized image.

## References
- http://www.securityfocus.com/bid/95841
- http://www.debian.org/security/2017/dsa-3777
- https://github.com/libgd/libgd/blob/gd-2.2.4/CHANGELOG.md
- https://github.com/libgd/libgd/commit/1846f48e5fcdde996e7c27a4bbac5d0aef183e4b
