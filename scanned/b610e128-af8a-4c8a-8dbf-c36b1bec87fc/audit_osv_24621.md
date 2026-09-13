# [M] CVE-2023-24056

## Summary
Severity: Medium
Advisory: CVE-2023-24056
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-01-22
Source: https://osv.dev/vulnerability/CVE-2023-24056
Type: osv

## Details
In pkgconf through 1.9.3, variable duplication can cause unbounded string expansion due to incorrect checks in libpkgconf/tuple.c:pkgconf_tuple_parse. For example, a .pc file containing a few hundred bytes can expand to one billion bytes.

## References
- https://gitea.treehouse.systems/ariadne/pkgconf/commit/628b2b2bafa5d3a2017193ddf375093e70666059
- https://github.com/pkgconf/pkgconf/tags
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/24xxx/CVE-2023-24056.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-24056
- https://nullprogram.com/blog/2023/01/18/
