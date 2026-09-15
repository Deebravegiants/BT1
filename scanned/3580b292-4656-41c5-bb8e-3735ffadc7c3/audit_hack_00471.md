# [M] Thetanuts Finance incident: A newly deployed vault contract of Thetanuts Finance was exploited via a First Depositor Attack. The attacker took advantage of th

## Summary
Severity: Medium
Target: Thetanuts Finance
Loss: $ 50,000
Attack method: Smart Contract Vulnerability
Published: 2026-04-20
Source: https://academy.teleswap.xyz/defi-protocol-hacks-april-2026-exploits-analyzed/
Type: slowmist-incident

## Details
A newly deployed vault contract of Thetanuts Finance was exploited via a First Depositor Attack. The attacker took advantage of the vault’s share calculation logic when totalAssets and totalSupply were both 0 at initialization: they deposited a minimal amount (e.g., 1 wei) to mint 1 share, then directly transferred a large amount of assets (e.g., ETH) to the contract, manipulating the asset-to-share ratio. When subsequent users deposited, they received almost no shares, allowing the attacker to redeem their single share for nearly all the vault’s assets. The loss was approximately $50,000. The protocol focuses on on-chain options and yield vaults; this incident affected a specific new vault.
