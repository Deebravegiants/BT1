# [M] Missing slippage check on curve's remove liquidity

## Summary
Severity: Medium
Contest weight: 0.4318
Dataset id: 6069
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
bytes4 private constant REMOVE_LIQUIDITY_2 =
    bytes4(keccak256("remove_liquidity(uint256,uint256[2])"));
bytes4 private constant REMOVE_LIQUIDITY_3 =
    bytes4(keccak256("remove_liquidity(uint256,uint256[3])"));
bytes4 private constant REMOVE_LIQUIDITY_4 =
    bytes4(keccak256("remove_liquidity(uint256,uint256[4])"));
bytes4 private constant REMOVE_LIQUIDITY_ZAPPER =
    bytes4(keccak256("remove_liquidity(address,uint256,uint256[4])"));

function _constructNCoinsDecreasePosition(
    uint256 nCoins,
    uint256 burnAmount
) private pure returns (bytes memory) {
    if (nCoins == 2) {
        return abi.encodeWithSelector(REMOVE_LIQUIDITY_2, burnAmount, [0, 0]); // <== example
    } else if (nCoins == 3) {
        return abi.encodeWithSelector(REMOVE_LIQUIDITY_3, burnAmount, [0, 0, 0]);
    } else {
        return abi.encodeWithSelector(REMOVE_LIQUIDITY_4, burnAmount, [0, 0, 0, 0]);
    }
}
```
The issue is that this constructs a remove_liquidity call with all minAmounts set to zero. This opens the possibility for the remove command to be sandwiched, where the expected token ratios do not match what would be received under normal conditions. The risk is heightened if a speciﬁc token in the pool enters a depletion scenario, where MEV bots compete to drain it. Since the current implementation accepts any ratio, this can result in signiﬁcant losses.

## Recommendation
Since most parameters are already constructed on the backend, consider including minAmounts as an input parameter. This would allow explicit control over slippage tolerance, enabling the setting of either high or low slippage thresholds.
