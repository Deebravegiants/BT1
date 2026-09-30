# [C] CVE-2018-12911

## Summary
Severity: Critical
Advisory: CVE-2018-12911
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-19
Source: https://osv.dev/vulnerability/CVE-2018-12911
Type: osv

## Details
WebKitGTK+ 2.20.3 has an off-by-one error, with a resultant out-of-bounds write, in the get_simple_globs functions in ThirdParty/xdgmime/src/xdgmimecache.c and ThirdParty/xdgmime/src/xdgmimeglob.c.

## References
- https://usn.ubuntu.com/3743-1/
- https://trac.webkit.org/changeset/233404/webkit
