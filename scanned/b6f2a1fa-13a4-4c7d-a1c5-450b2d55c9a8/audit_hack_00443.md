# [M] Butter Bridge incident: The Butter Bridge V3.1 (part of MAP Protocol and Butter Network) was exploited. An attacker used a vulnerability in the OmniServic

## Summary
Severity: Medium
Target: Butter Bridge
Loss: $ 180,000
Attack method: Smart Contract Vulnerability
Published: 2026-05-20
Source: https://ourcryptotalk.com/news/butter-bridge-exploit-mints-1-quadrillion-mapo-tokens
Type: slowmist-incident

## Details
The Butter Bridge V3.1 (part of MAP Protocol and Butter Network) was exploited. An attacker used a vulnerability in the OmniServiceProxy contract’s retry message verification logic, specifically an abi.encodePacked hash collision with dynamic-bytes fields. This allowed forging a cross-chain retry message that bypassed authentication, resulting in the minting of approximately 1 quadrillion (10^15) MAPO tokens (about 4.8 million times the legitimate ~208 million circulating supply). The attacker dumped ~1 billion fake MAPO into the Uniswap V4 ETH/MAPO pool, extracting roughly $180,000 in liquidity (≈52.21 ETH). The teams immediately paused the bridge and related swaps. User funds in pending swaps are safe, and a patch/audit/redeployment is in progress. The remaining ~999 trillion fake tokens stay in the attacker’s wallet, posing ongoing dilution risk.
