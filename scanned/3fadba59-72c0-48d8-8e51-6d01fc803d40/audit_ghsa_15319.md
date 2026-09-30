# [M] Miniscript allows stack consumption

## Summary
Severity: Medium
Advisory: GHSA-rv9v-r4vm-gj8x
CVE: CVE-2024-44073
CWE: CWE-674, CWE-770, CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-08-19
Source: https://github.com/advisories/GHSA-rv9v-r4vm-gj8x
Type: github-advisory

## Affected
- crates.io: `miniscript` — affected >=12.0.0 <12.2.0
- crates.io: `miniscript` — affected >=11.0.0 <11.2.0
- crates.io: `miniscript` — affected >=10.0.0 <10.2.0
- crates.io: `miniscript` — affected >=0 <9.2.0

## Details
The Miniscript (aka rust-miniscript) library for Rust allows stack consumption because it does not properly track tree depth.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-44073
- https://github.com/rust-bitcoin/rust-miniscript/pull/704
- https://github.com/rust-bitcoin/rust-miniscript/pull/712
- https://github.com/rust-bitcoin/rust-miniscript/pull/712/files
- https://github.com/rust-bitcoin/rust-miniscript/pull/713/files
- https://github.com/rust-bitcoin/rust-miniscript/pull/714/files
- https://github.com/rust-bitcoin/rust-miniscript/pull/715/files
- https://github.com/rust-bitcoin/rust-miniscript/commit/5b0f5e3417f027a22b066debf825dbe6644b575b
- https://github.com/rust-bitcoin/rust-miniscript/commit/8f54b5e3fb7129ed9fbed53f1cb9e6e62ea4c151
- https://github.com/rust-bitcoin/rust-miniscript/compare/11.2.0...12.2.0
