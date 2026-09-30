# [M] `_computeAvailable

## Summary
Severity: Medium
Contest weight: 0.6316
Dataset id: 19200
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the internal accounting routine that calculates how many tokens are currently available for liquidation. The function adds a newly accrued amount (deltaAmount) to the previously stored available balance (boost.available) and returns the sum. To prevent the result from exceeding the contract’s actual token holdings, the code attempts to cap deltaAmount by comparing it with the contract’s total token balance. However, the comparison is performed against the full balance instead of the balance that remains after subtracting the already‑accounted boost.available. As a result, when boost.available is non‑zero, the returned value can be larger than the contract’s real token balance. This over‑estimation propagates to liquidation logic, where the protocol calls liquidate with a number that the contract cannot transfer, causing the transfer to revert. The impact is that liquidation attempts fail, users may see transactions revert or receive no funds, and the protocol’s accounting assumptions are broken because the system believes more tokens are available than actually exist. The bug manifests whenever time has elapsed (deltaTime > 0) and the accrued deltaAmount plus the stored available amount exceeds the contract’s token balance. It primarily affects token holders and liquidators who rely on accurate available balances, and it can also stall the protocol’s risk‑management mechanisms. The issue was discovered during a security audit that exercised the liquidation path and observed mismatched balances. It is subtle because the function returns a plausible numeric value and the erroneous cap does not trigger an immediate overflow; the failure only appears when the inflated amount is used in a transfer. To remediate, the cap should be applied to the difference between the contract’s current token balance and boost.available, ensuring that boost.available + deltaAmount never exceeds the actual balance. This correction restores the invariant that the reported available amount is always bounded by the contract’s holdings, aligning the implementation with the intended accounting model and preventing liquidation reverts.

## Proof of Concept
`VaultBooster._computeAvailable()` used to count the number of `tokens` currently available.  
There are two conditions:

1. `accrue` continuously according to time  
2. the final cumulative value cannot be greater than the current contract balance

The code is as follows:
    
```solidity
function _computeAvailable(IERC20 _tokenOut) internal view returns (uint256) {
    Boost memory boost = _boosts[_tokenOut];
    uint256 deltaTime = block.timestamp - boost.lastAccruedAt;
    uint256 deltaAmount;
    if (deltaTime == 0) {
        return boost.available;
    }
    if (boost.tokensPerSecond > 0) {
        deltaAmount = boost.tokensPerSecond * deltaTime;
    }
    if (boost.multiplierOfTotalSupplyPerSecond.unwrap() > 0) {
        uint256 totalSupply = twabController.getTotalSupplyTwabBetween(address(vault), uint32(boost.lastAccruedAt), uint32(block.timestamp));
        deltaAmount += convert(boost.multiplierOfTotalSupplyPerSecond.intoUD60x18().mul(convert(deltaTime)).mul(convert(totalSupply)));
    }
    uint256 availableBalance = _tokenOut.balanceOf(address(this));
    deltaAmount = availableBalance > deltaAmount ? deltaAmount : availableBalance;
    return boost.available + deltaAmount;
}
```

The current implementation code, limiting the maximum value of `deltaAmount` is wrong, using the minimum value compared to the current balance `_tokenOut.balanceOf(address(this))`.

But the current balance includes the previously accumulated `boost.available`, so normally it should be compared to the difference between the current balance and `boost.available`.

So the value returned may be larger than the current balance, and `LiquidationPair.sol` performs `source.liquidatableBalanceOf()` and `source.liquidate()` with too large a number, resulting in a failed transfer.

## Recommendation
The maximum value returned should not exceed the current balance
    
```solidity
function _computeAvailable(IERC20 _tokenOut) internal view returns (uint256) {
    Boost memory boost = _boosts[_tokenOut];
    uint256 deltaTime = block.timestamp - boost.lastAccruedAt;
    uint256 deltaAmount;
    if (deltaTime == 0) {
        return boost.available;
    }
    if (boost.tokensPerSecond > 0) {
        deltaAmount = boost.tokensPerSecond * deltaTime;
    }
    if (boost.multiplierOfTotalSupplyPerSecond.unwrap() > 0) {
        uint256 totalSupply = twabController.getTotalSupplyTwabBetween(address(vault), uint32(boost.lastAccruedAt), uint32(block.timestamp));
        deltaAmount += convert(boost.multiplierOfTotalSupplyPerSecond.intoUD60x18().mul(convert(deltaTime)).mul(convert(totalSupply)));
    }
    uint256 availableBalance = _tokenOut.balanceOf(address(this));
    deltaAmount = availableBalance > deltaAmount ? deltaAmount : availableBalance;
    return boost.available + deltaAmount;
}
```
