# [H] Converter Permission Bypass with MilkyMaker::convertMultiple()

## Summary
Severity: High
Contest weight: 0.7568
Dataset id: 12514
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the MilkySwap protocol, the MilkyMaker contract is designed to trade tokens collected from fees for MILKY and serves up rewards for CREAMY holders. Speciﬁcally, the convert() routine is implemented to swap tokens and it has a permission check of whether the msg.sender is an authorized converter. To elaborate, we show below its full implementation.
```solidity
function convert(address token0, address token1) external onlyEOA {
    require(_converters[msg.sender], "sender not authorized to call convert");
    _convert(token0, token1);
}
```
It comes to our attention that the permission check for converter is not applied in the convertMultiple() routine, which is initially designed to save gas when the converter has multiple token pairs to convert. A bad actor could call the convertMultiple() routine to force the MilkyMaker contract to remove liquidity and swap in a manipulated imbalance pool to exploit.
```solidity
function convertMultiple(
    address[] calldata token0,
    address[] calldata token1
) external onlyEOA {
    // TODO: This can be optimized a fair bit, but this is safer and simpler for now
    uint256 len = token0.length;
    for (uint256 i = 0; i < len; i++) {
        _convert(token0[i], token1[i]);
    }
}
```

## Recommendation
Add the same permission check for converter in the convertMultiple() routine.
