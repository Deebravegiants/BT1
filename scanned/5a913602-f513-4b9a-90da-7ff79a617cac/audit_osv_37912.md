# [C] Compress::Raw::Zlib versions through 2.219 for Perl use potentially insecure versions of zlib

## Summary
Severity: Critical
Advisory: CVE-2026-3381
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-05
Source: https://osv.dev/vulnerability/CVE-2026-3381
Type: osv

## Details
Compress::Raw::Zlib versions through 2.219 for Perl use potentially insecure versions of zlib.

Compress::Raw::Zlib includes a copy of the zlib library. Compress::Raw::Zlib version 2.220 includes zlib 1.3.2, which addresses findings fron the 7ASecurity audit of zlib. The includes fixs for CVE-2026-27171.

## References
- https://cpan.org/modules
- https://www.zlib.net/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/3xxx/CVE-2026-3381.json
- https://github.com/madler/zlib/releases/tag/v1.3.2
- https://metacpan.org/release/PMQS/Compress-Raw-Zlib-2.221/source/Changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-3381
- https://www.cve.org/CVERecord?id=CVE-2026-27171
- https://github.com/pmqs/Compress-Raw-Zlib/issues/41
- https://github.com/madler/zlib
- https://github.com/pmqs/Compress-Raw-Zlib
- https://7asecurity.com/blog/2026/02/zlib-7asecurity-audit/
