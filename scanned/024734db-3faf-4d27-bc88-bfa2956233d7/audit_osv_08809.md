# [M] CVE-2016-6214

## Summary
Severity: Medium
Advisory: CVE-2016-6214
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-08-12
Source: https://osv.dev/vulnerability/CVE-2016-6214
Type: osv

## Details
gd_tga.c in the GD Graphics Library (aka libgd) before 2.2.3 allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted TGA file.

## References
- http://lists.opensuse.org/opensuse-updates/2016-08/msg00086.html
- http://lists.opensuse.org/opensuse-updates/2016-09/msg00078.html
- http://www.debian.org/security/2016/dsa-3619
- http://www.openwall.com/lists/oss-security/2016/07/13/12
- http://www.openwall.com/lists/oss-security/2016/07/13/5
- http://www.ubuntu.com/usn/USN-3060-1
- https://github.com/libgd/libgd/issues/247#issuecomment-232084241
- https://libgd.github.io/release-2.2.3.html
- https://github.com/libgd/libgd/commit/10ef1dca63d62433fda13309b4a228782db823f7
