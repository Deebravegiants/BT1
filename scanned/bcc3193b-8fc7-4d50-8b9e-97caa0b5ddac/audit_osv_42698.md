# [H] Text::Minify::XS versions from 0.3.0 before 0.7.8 for Perl have heap overflow when processing some malformed UTF-8 characters

## Summary
Severity: High
Advisory: CVE-2026-7040
Aliases: GHSA-jqhf-vv4h-77h2
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/CVE-2026-7040
Type: osv

## Details
Text::Minify::XS versions from 0.3.0 before 0.7.8 for Perl have a heap overflow when processing some malformed UTF-8 characters.

The minify functions mishandled some malformed UTF-8 characters, leading to heap corruption.

Note that the minify_utf8 function is an alias for minify.

## References
- http://www.openwall.com/lists/oss-security/2026/04/27/5
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/7xxx/CVE-2026-7040.json
- https://github.com/robrwo/Text-Minify-XS/security/advisories/GHSA-jqhf-vv4h-77h2
- https://metacpan.org/release/RRWO/Text-Minify-XS-v0.7.8/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-7040
- https://github.com/robrwo/Text-Minify-XS
