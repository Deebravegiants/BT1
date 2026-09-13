# [M] CVE-2017-9204

## Summary
Severity: Medium
Advisory: CVE-2017-9204
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-23
Source: https://osv.dev/vulnerability/CVE-2017-9204
Type: osv

## Details
The iw_get_ui16le function in imagew-util.c:405:23 in libimageworsener.a in ImageWorsener 1.3.1 allows remote attackers to cause a denial of service (invalid read and SEGV) via a crafted image, related to imagew-jpeg.c.

## References
- https://blogs.gentoo.org/ago/2017/05/20/imageworsener-multiple-vulnerabilities/
- https://github.com/jsummers/imageworsener/commit/b45cb1b665a14b0175b9cb1502ef7168e1fe0d5d
