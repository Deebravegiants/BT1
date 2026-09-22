# [M] ERC721Consecutive incorrect balance update with batch of 1

## Summary
Severity: Medium
Chain: Solidity
Component: OpenZeppelin/openzeppelin-contracts
CVE: CVE-2023-26488
Published: 2023-03-02
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/security/advisories/GHSA-878m-3g6q-594q
Type: github-advisory

## Details
### Impact

The ERC721Consecutive contract designed for minting NFTs in batches does not update balances when a batch has size 1 and consists of a single token. Subsequent transfers from the receiver of that token may overflow the balance as reported by `balanceOf`.

The issue exclusively presents with batches of size 1.

### Patches

The issue has been patched in 4.8.2.

<!-- ### References -->
