# [H] Potential 99.5% loss in `emergencyWithdraw`

## Summary
Severity: High
Contest weight: 0.1266
Dataset id: 19104
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
99.5% of user funds are lost to slippage in two Yieldbox strategies in case of [`emergencyWithdraw()`](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/convex/ConvexTricryptoStrategy.sol#L148-L156)

## Recommendation
Fix the incorrect `minAmount` calculation to be `uint256 minAmount = calcAmount - (calcAmount * 50) / 10_000;` in [ConvexTriCryptoStrategy](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/convex/ConvexTricryptoStrategy.sol#L154) and [LidoEthStrategy](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/lido/LidoEthStrategy.sol#L108).
