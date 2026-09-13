# [H] Sereal::Decoder versions from 4.000 through 4.009_002 for Perl embeds a vulnerable version of the Zstandard library

## Summary
Severity: High
Advisory: CVE-2024-14030
Aliases: CVE-2024-14031, GHSA-w77f-wv46-4vcx
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2024-14030
Type: osv

## Details
Sereal::Decoder versions from 4.000 through 4.009_002 for Perl embeds a vulnerable version of the Zstandard library.

Sereal::Decoder embeds a version of the Zstandard (zstd) library that is vulnerable to CVE-2019-11922.  This is a race condition in the one-pass compression functions of Zstandard prior to version 1.3.8 could allow an attacker to write bytes out of bounds if an output buffer smaller than the recommended size was used.

## References
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/14xxx/CVE-2024-14030.json
- https://github.com/advisories/GHSA-w77f-wv46-4vcx
- https://metacpan.org/release/YVES/Sereal-Decoder-4.010/changes
- https://nvd.nist.gov/vuln/detail/CVE-2024-14030
- https://www.cve.org/CVERecord?id=CVE-2019-11922
- https://github.com/Sereal/Sereal
