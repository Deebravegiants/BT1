# [H] Uncontrolled recursion in rust-yaml

## Summary
Severity: High
Advisory: GHSA-hv87-47h9-jcvq
CVE: CVE-2018-20993
CWE: CWE-674
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-hv87-47h9-jcvq
Type: github-advisory

## Affected
- crates.io: `yaml-rust` — affected >=0 <0.4.1

## Details
Affected versions of this crate did not prevent deep recursion while deserializing data structures. This allows an attacker to make a YAML file with deeply nested structures that causes an abort while deserializing it. The flaw was corrected by checking the recursion depth.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20993
- https://github.com/chyh1990/yaml-rust/pull/109
- https://github.com/chyh1990/yaml-rust/commit/d61b49cb90391fc4f7f72a1abe597476c8651a07
- https://github.com/chyh1990/yaml-rust
- https://rustsec.org/advisories/RUSTSEC-2018-0006.html
