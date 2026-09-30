# [H] H-03 | Third Party Liquidity Results In DoS

## Summary
Severity: High
Contest weight: 0.1587
Dataset id: 2021
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The removeAllFrom function in the BPOOL contract reports the entirety of third party liquidity as fees
when the liquidityToRemove > currentLiquidity, however the excess liquidity is burned from the
msg.sender in the _removeLiquidity function.
This means that the calling contract will think it has more bAssets than it does because the reported
bAssetFees_ includes an amount that was burnt from the sender.
During rebalances this results in an underflow DoS when ultimately attempting to send more
bAssets than the contract holds to the fee receiver for bAssetFees_.

## Recommendation
Do not burn the bAssets from the msg.sender in the _removeLiquidity function when removing third
party liquidity.
