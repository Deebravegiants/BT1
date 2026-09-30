# [H] Attackers can include other users nullifiers to make their funds stuck when adding liquidity to curve

## Summary
Severity: High
Contest weight: 0.1052
Dataset id: 15196
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
CurveLiquidityAssetManager::curveAddLiquidity() always spends the nullifiers, even if the amounts used are 0. In the circuit, if the amount is 0, it does not validate the nullifier against the user signature, making it possible to include nullifiers from other users in the same transaction and losing their funds forever. Here is the poc.

## Recommendation
In CurveAddLiquidityAssetManager::_addLiquidity() skip _postWithdraw() if the amount is 0.
