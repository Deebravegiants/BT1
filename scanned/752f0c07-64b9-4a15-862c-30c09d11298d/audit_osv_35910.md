# [C] TOML::XS versions before 0.06 for Perl bundle an unsupported and vulnerable version of tomlc99

## Summary
Severity: Critical
Advisory: CVE-2026-16634
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-16634
Type: osv

## Details
TOML::XS versions before 0.06 for Perl bundle an unsupported and vulnerable version of tomlc99.

The tomlc99 library is no longer maintained, and has an uncontrolled recursion vulnerability publicly reported in the issue tracker.

Any caller that passes untrusted TOML to from_toml risks a stack overflow from a deeply-nested document.

TOML::XS version 0.06 or later uses the successor tomlc17 library.

## References
- http://www.openwall.com/lists/oss-security/2026/07/24/4
- https://cpan.org/modules
- https://raw.githubusercontent.com/cktan/tomlc99/29076dfd095bbbbd50a3c1b2760d29f4b83e74ac/README.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/16xxx/CVE-2026-16634.json
- https://metacpan.org/release/FELIPE/TOML-XS-0.06/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-16634
- https://github.com/cktan/tomlc99/issues/97
- https://github.com/FGasper/p5-TOML-XS
- https://github.com/cktan/tomlc17
- https://toml.io/en/v1.0.0
