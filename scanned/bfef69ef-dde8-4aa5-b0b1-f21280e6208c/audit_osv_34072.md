# [H] Polkadot Frontier contains silent failure in Curve25519 arithmetic precompiles with malformed points

## Summary
Severity: High
Advisory: CVE-2025-54426
Aliases: GHSA-v4q3-23rh-w5mw
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:H/SA:N)
Published: 2025-07-28
Source: https://osv.dev/vulnerability/CVE-2025-54426
Type: osv

## Details
Polkadot Frontier is an Ethereum and EVM compatibility layer for Polkadot and Substrate. In versions prior to commit 36f70d1, the Curve25519Add and Curve25519ScalarMul precompiles incorrectly handle invalid Ristretto point representations. Instead of returning an error, they silently treat invalid input bytes as the Ristretto identity element, leading to potentially incorrect cryptographic results. This is fixed in commit 36f70d1.

## References
- https://dotpal.io/assets/files/frontier-srlabs-2505-718c3bfa5df9fed1862fed05de506859.pdf
- https://github.com/polkadot-evm/frontier/pull/1720/commits/8ed6053fb868495477ba2409f7e64f439df76f96
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54426.json
- https://github.com/polkadot-evm/frontier/security/advisories/GHSA-v4q3-23rh-w5mw
- https://nvd.nist.gov/vuln/detail/CVE-2025-54426
- https://github.com/polkadot-evm/frontier/commit/36f70d1defcaeaed5a453015f6c98c21bb5b121b
