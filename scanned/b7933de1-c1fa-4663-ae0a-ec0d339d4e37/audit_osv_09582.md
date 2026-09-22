# [M] CVE-2017-1000211

## Summary
Severity: Medium
Advisory: CVE-2017-1000211
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2017-11-17
Source: https://osv.dev/vulnerability/CVE-2017-1000211
Type: osv

## Details
Lynx before 2.8.9dev.16 is vulnerable to a use after free in the HTML parser resulting in memory disclosure, because HTML_put_string() can append a chunk onto itself.

## References
- http://www.securityfocus.com/bid/102180
- https://lists.debian.org/debian-lts-announce/2017/11/msg00021.html
- http://lynx.invisible-island.net/current/CHANGES.html
- https://github.com/ThomasDickey/lynx-snapshots/commit/280a61b300a1614f6037efc0902ff7ecf17146e9
