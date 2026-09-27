# [M] CVE-2016-6163

## Summary
Severity: Medium
Advisory: CVE-2016-6163
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-03
Source: https://osv.dev/vulnerability/CVE-2016-6163
Type: osv

## Details
The rsvg_pattern_fix_fallback function in rsvg-paint_server.c in librsvg2 2.40.2 allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted svg file.

## References
- http://www.openwall.com/lists/oss-security/2016/07/04/3
- http://www.openwall.com/lists/oss-security/2016/07/05/9
- https://bugzilla.redhat.com/show_bug.cgi?id=1353520
