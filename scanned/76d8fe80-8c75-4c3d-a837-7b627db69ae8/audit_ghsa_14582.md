# [M] OpenZeppelin Contracts contains Incorrect Calculation

## Summary
Severity: Medium
Advisory: GHSA-878m-3g6q-594q
CVE: CVE-2023-26488
CWE: CWE-682
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-03-03
Source: https://github.com/advisories/GHSA-878m-3g6q-594q
Type: github-advisory

## Affected
- npm: `@openzeppelin/contracts` — affected >=4.8.0 <4.8.2
- npm: `@openzeppelin/contracts-upgradeable` — affected >=4.8.0 <4.8.2

## Details
### Impact

The ERC721Consecutive contract designed for minting NFTs in batches does not update balances when a batch has size 1 and consists of a single token. Subsequent transfers from the receiver of that token may overflow the balance as reported by `balanceOf`.

The issue exclusively presents with batches of size 1.

### Patches

The issue has been patched in 4.8.2.

<!-- ### References -->

## References
- https://github.com/OpenZeppelin/openzeppelin-contracts/security/advisories/GHSA-878m-3g6q-594q
- https://nvd.nist.gov/vuln/detail/CVE-2023-26488
- https://github.com/OpenZeppelin/openzeppelin-contracts/commit/167bf67ed3907f4a674043496019fa346cee7705
- https://github.com/OpenZeppelin/openzeppelin-contracts
- https://github.com/OpenZeppelin/openzeppelin-contracts/releases/tag/v4.8.2
