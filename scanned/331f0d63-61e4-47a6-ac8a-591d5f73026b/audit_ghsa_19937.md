# [H] Creator Verification Error when Bubblegum Activate

## Summary
Severity: High
Advisory: GHSA-8r76-fr72-j32w
Ecosystem: crates.io
Published: 2022-12-12
Source: https://github.com/advisories/GHSA-8r76-fr72-j32w
Type: github-advisory

## Affected
- crates.io: `mpl-bubblegum` — affected >=0 <0.6.0
- crates.io: `mpl-token-metadata` — affected >=1.5.0 <1.6.3

## Details
This was an error found by @metamania01 of the Audit Company Solshield.

It allowed one to verify a creator that did not sign by making use of a provision in Token Metadata that allows Creators who have signed compressed nfts to allow them to decompress with verified creators.

The issue is now patched.
For more info see.
https://twitter.com/thehasheddude/status/1601642138143375360

## References
- https://github.com/metaplex-foundation/metaplex-program-library/security/advisories/GHSA-8r76-fr72-j32w
- https://github.com/metaplex-foundation/metaplex-program-library/commit/c18591a7ce9bb561940cb94df4b7c35ef9cc0f57
- https://github.com/metaplex-foundation/metaplex-program-library
- https://twitter.com/thehasheddude/status/1601642138143375360
