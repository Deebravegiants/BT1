# [C] Perl versions from 5.9.4 before 5.40.4-RC1, from 5.41.0 before 5.42.2-RC1, from 5.43.0 before 5.43.9 contain a vulnerable version of Compress::Raw::Zlib

## Summary
Severity: Critical
Advisory: CVE-2026-4176
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-29
Source: https://osv.dev/vulnerability/CVE-2026-4176
Type: osv

## Details
Perl versions from 5.9.4 before 5.40.4-RC1, from 5.41.0 before 5.42.2-RC1, from 5.43.0 before 5.43.9 contain a vulnerable version of Compress::Raw::Zlib.

Compress::Raw::Zlib is included in the Perl package as a dual-life core module, and is vulnerable to CVE-2026-3381 due to a vendored version of zlib which has several vulnerabilities, including CVE-2026-27171. The bundled Compress::Raw::Zlib was updated to version 2.221 in Perl blead commit c75ae9cc164205e1b6d6dbd57bd2c65c8593fe94.

## References
- http://www.openwall.com/lists/oss-security/2026/03/30/2
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/4xxx/CVE-2026-4176.json
- https://lists.security.metacpan.org/cve-announce/msg/37638919/
- https://metacpan.org/release/PMQS/Compress-Raw-Zlib-2.221/source/Changes
- https://metacpan.org/release/SHAY/perl-5.40.4/changes
- https://metacpan.org/release/SHAY/perl-5.42.2/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-4176
- https://www.cve.org/CVERecord?id=CVE-2026-3381
- https://github.com/Perl/perl5/commit/c75ae9cc164205e1b6d6dbd57bd2c65c8593fe94
- https://github.com/Perl/perl5
