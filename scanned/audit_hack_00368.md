# [M] Swan Treasury incident: The decentralized asset management protocol Swan Treasury on BNB Chain was exploited due to the leakage of an off-chain signer's p

## Summary
Severity: Medium
Target: Swan Treasury
Loss: $ 625,000
Attack method: Private Key Leakage
Published: 2026-07-30
Source: https://x.com/DefimonAlerts/status/2083039796784410802
Type: slowmist-incident

## Details
The decentralized asset management protocol Swan Treasury on BNB Chain was exploited due to the leakage of an off-chain signer's private key (the _signer key hardcoded in the ZhaiquanBuy contract). The attacker forged valid signatures and used PancakeSwap flash loans to purchase approximately 687,000 STY tokens at around a 100x discount (spending approximately 19,700 USDT). The attacker then forged the related claim()/transfer signatures and dumped the tokens into the STY/USDT pool, making a profit of approximately $625,000.
