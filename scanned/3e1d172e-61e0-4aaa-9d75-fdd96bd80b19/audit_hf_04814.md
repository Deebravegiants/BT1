# [M] Swapping large amounts of assets back and

## Summary
Severity: Medium
Contest weight: 0.4337
Dataset id: 22684
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Swapping large amounts of assets back and forth in an Aerodrome pool allows to bypass exposure limits.
The WrappedAerodromeAM allows wrapping LPs of an Aerodrome pool to then deposit the wrapped position as collateral in an Arcadia account. The wrapper accounts for the trading fees accumulated by the LP when estimating the value of the collateral:
```solidity
(uint256 positionId) = _getAssetFromKey(assetKey);
(uint256 fee0Position, uint256 fee1Position) = feesOf(positionId);
underlyingAssetsAmounts = new uint256[](3);
underlyingAssetsAmounts[0] = positionState[positionId].amountWrapped;
underlyingAssetsAmounts[1] = fee0Position;
underlyingAssetsAmounts[2] = fee1Position;
```
It's possible to take advantage of this to bypass exposure limits. An attacker can:
1. Create a new Aerodrome pool
2. Mint LPs, the attacker owns the whole liquidity supply
3. Deposit the LP as collateral via WrappedAerodromeAM
4. Swap large amounts in the Aerodrome pool back and forth to increase the fees accumulated by the LP. The value of the collateral increases while the collateral is already deposited. The attacker won't lose anything besides gas fees because he controls the whole (minues 1e3) liquidity supply.
An attacker can keep swapping amounts indefinitely. Because this is done while the collateral is already deposited in the account the attacker can avoid the restrictions of exposure limits.
Exposure limits can be bypassed.

## Recommendation
A similar attack is possible on UniswapV3 positions, however in that case the protocol already implements safety guards against this possibility. Implement a similar safety guard for Aerodrome positions as well.
