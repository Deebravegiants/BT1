# [C] CVE-2016-5116

## Summary
Severity: Critical
Advisory: CVE-2016-5116
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2016-08-07
Source: https://osv.dev/vulnerability/CVE-2016-5116
Type: osv

## Details
gd_xbm.c in the GD Graphics Library (aka libgd) before 2.2.0, as used in certain custom PHP 5.5.x configurations, allows context-dependent attackers to obtain sensitive information from process memory or cause a denial of service (stack-based buffer under-read and application crash) via a long name.

## References
- http://lists.opensuse.org/opensuse-updates/2016-09/msg00078.html
- http://www.debian.org/security/2016/dsa-3619
- http://www.ubuntu.com/usn/USN-3030-1
- https://github.com/libgd/libgd/issues/211
- https://github.com/libgd/libgd/commit/4dc1a2d7931017d3625f2d7cff70a17ce58b53b4
- http://www.openwall.com/lists/oss-security/2016/05/29/5
