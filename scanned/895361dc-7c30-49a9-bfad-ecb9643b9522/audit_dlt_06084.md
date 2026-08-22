# [?] Fix potential vulnerabilities in programs using spl-token CPIs by adding program id checks (#1714)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-program/token
Published: 2021-05-12
Source: https://github.com/solana-program/token/commit/38751ab1fd22c8cf6e9e14575905242753cf591a
Type: security-commit

## Details
Fix potential vulnerabilities in programs using spl-token CPIs by adding program id checks (#1714)

* Add spl-token program id check helper function. Add program id to instruction bindings.

* Run cargo fmt

* Fixup tests

* Skip ATA tests when custom token program-id

Co-authored-by: Tyera Eulberg <tyera@solana.com>
