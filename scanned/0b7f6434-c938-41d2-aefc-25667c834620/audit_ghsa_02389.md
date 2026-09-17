# [C] OS command injection in ripgrep

## Summary
Severity: Critical
Advisory: GHSA-g4xg-fxmg-vcg5
CVE: CVE-2021-3013
CWE: CWE-78
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-05
Source: https://github.com/advisories/GHSA-g4xg-fxmg-vcg5
Type: github-advisory

## Affected
- crates.io: `ripgrep` — affected >=0 <13.0.0
- crates.io: `grep-cli` — affected >=0 <0.1.6

## Details
ripgrep before 13 on Windows allows attackers to trigger execution of arbitrary programs from the current working directory via the -z/--search-zip or --pre flag.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3013
- https://github.com/BurntSushi/ripgrep/issues/1773
- https://github.com/BurntSushi/ripgrep
- https://github.com/BurntSushi/ripgrep/blob/e48a17e1891e1ea9dd06ba0e48d5fb140ca7c0c4/CHANGELOG.md
- https://github.com/BurntSushi/ripgrep/blob/master/CHANGELOG.md
- https://github.com/BurntSushi/ripgrep/blob/master/CHANGELOG.md#1300-2021-06-12
- https://rustsec.org/advisories/RUSTSEC-2021-0071.html
