# [M] `SpeedBumpPriceGate.sol#addGate

## Summary
Severity: Medium
Contest weight: 0.3743
Dataset id: 6674
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
gate.priceIncreaseDenominator = priceIncreaseDenominator;

If `priceIncreaseDenominator` is set to `0` when `addGate()`, in `passThruGate()` the tx will revert at L72 because of div by 0.

```solidity
// multiply by the price increase factor
gate.lastPrice = (price * gate.priceIncreaseFactor) / gate.priceIncreaseDenominator;
```

## Recommendation
Consider adding a check in `addGate()` to require `priceIncreaseDenominator > 0`.

This is fine, we just add another gate, redeploy the tree and only harm done is we lost some gas.

While value is not leaked in this instance, this can cause functionality to be interrupted until fixed. Severity of issue will be maintained.
