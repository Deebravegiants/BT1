# [H] CVE-2015-8875

## Summary
Severity: High
Advisory: CVE-2015-8875
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-06-01
Source: https://osv.dev/vulnerability/CVE-2015-8875
Type: osv

## Details
Multiple integer overflows in the (1) pixops_composite_nearest, (2) pixops_composite_color_nearest, and (3) pixops_process functions in pixops/pixops.c in gdk-pixbuf before 2.33.1 allow remote attackers to cause a denial of service (application crash) or possibly execute arbitrary code via a crafted image, which triggers a heap-based buffer overflow.

## References
- http://www.debian.org/security/2016/dsa-3589
- http://www.ubuntu.com/usn/USN-3085-1
- http://www.openwall.com/lists/oss-security/2016/05/12/3
- http://www.openwall.com/lists/oss-security/2016/05/16/1
- http://www.openwall.com/lists/oss-security/2016/05/17/7
- https://git.gnome.org/browse/gdk-pixbuf/commit/?id=dbfe8f70471864818bf458a39c8a99640895bd22
