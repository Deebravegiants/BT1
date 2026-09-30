# [M] M-3 An incorrect interface version deﬁnition

## Summary
Severity: Medium
Contest weight: 0.0684
Dataset id: 6754
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
• CurveHandler.sol#L183
If interfaceVersion == 0, version0removeliquidityone_coin is called in CurveHandler.
The following pools were found in the project with 0:
• REN_BTC (0x930541...eDf0895B)
• SUSDDAIUSDT_USDC (0xA5407e...C53efBfD)
All pools are considered as version 0, but in RENBTC there is a removeliquidityonecoin method.
So, there is no need to use version0removeliquidityonecoin for REN_BTC.

## Recommendation
We recommend revising the pool versioning process (CurveRegistryCache.sol#L235).
