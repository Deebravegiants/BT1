# [H] Data races in lexer

## Summary
Severity: High
Advisory: GHSA-f997-8gxg-r354
CVE: CVE-2020-36458
CWE: CWE-362, CWE-77
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-f997-8gxg-r354
Type: github-advisory

## Affected
- crates.io: `lexer` — affected >=0

## Details
lexer is a plugin based lexical reader.Affected versions of this crate implements Sync for ReaderResult<T, E> with the trait bound T: Send, E: Send. Since matching on the public enum ReaderResult<T, E> provides access to &T & &E, allowing data race to a non-Sync type T or E. This can result in a memory corruption when multiple threads concurrently access &T or &E. Suggested fix for the bug is change the trait bounds imposed on T & E to be T: Sync, E: Sync.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36458
- https://gitlab.com/nathanfaucett/rs-lexer
- https://gitlab.com/nathanfaucett/rs-lexer/-/issues/2
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/lexer/RUSTSEC-2020-0138.md
- https://rustsec.org/advisories/RUSTSEC-2020-0138.html
