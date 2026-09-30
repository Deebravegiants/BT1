# [M] CVE-2016-6911

## Summary
Severity: Medium
Advisory: CVE-2016-6911
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-01-26
Source: https://osv.dev/vulnerability/CVE-2016-6911
Type: osv

## Details
The dynamicGetbuf function in the GD Graphics Library (aka libgd) before 2.2.4 allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted TIFF image.

## References
- http://www.securityfocus.com/bid/95840
- http://www.debian.org/security/2016/dsa-3693
- https://github.com/libgd/libgd/blob/gd-2.2.4/CHANGELOG.md
- https://github.com/libgd/libgd/commit/4859d69e07504d4b0a4bdf9bcb4d9e3769ca35ae
- https://github.com/libgd/libgd/pull/353
