# [M] LoopStrategy is vulnerable to inflation attacks

## Summary
Severity: Medium
Contest weight: 0.3855
Dataset id: 10563
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
LoopStrategy inherits ERC4626Upgradeable, which calculates shares deposited as (_decimalsOffset() is 0):
shares = assets * (totalSupply() + 1) / (totalAssets() + 1);
As such, the following attack is possible:
- User deposits 1e18 assets.
- Attacker frontruns and deposits 1 asset, minting 1 * 1 / 1 = 1 share.
- Attacker donates 2e18 worth of vault shares to the market.
- User1 deposits 1e18 assets and receives no shares, shares = 1e18 * 2 / (2e18 + 1) = 0.
- User2 deposits 1.5e18 assets and receives no shares, shares = 1.5e18 * 2 / (3e18 + 1) = 0.
- Attacker redeems 1 * (4.5e18 + 1) / (1+1) = 2.25e18.
```

## Recommendation
Consider using a bigger decimals offset or do an initial deposit.
