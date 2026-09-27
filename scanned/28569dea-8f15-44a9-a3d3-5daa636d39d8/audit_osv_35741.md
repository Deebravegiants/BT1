# [M] CSS::Minifier::XS versions before 0.14 for Perl have a memory leak when the entire document is minified away

## Summary
Severity: Medium
Advisory: CVE-2026-13593
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-13593
Type: osv

## Details
CSS::Minifier::XS versions before 0.14 for Perl have a memory leak when the entire document is minified away.

The minify function has a memory leak when processing a document containing only characters to be removed, such as comments and whitespace.

## References
- http://www.openwall.com/lists/oss-security/2026/06/29/18
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/13xxx/CVE-2026-13593.json
- https://metacpan.org/release/GTERMARS/CSS-Minifier-XS-0.14/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-13593
- https://github.com/bleargh45/CSS-Minifier-XS
