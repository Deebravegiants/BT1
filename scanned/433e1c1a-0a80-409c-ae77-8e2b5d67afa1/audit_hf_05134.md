# [M] The repayment process in the

## Summary
Severity: Medium
Contest weight: 0.5952
Dataset id: 23181
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users can supply assets to the pools through the NFTPositionManager to earn rewards in zero tokens. Functions like deposit, withdraw, repay, and borrow should operate normally. However, due to an additional check, repayments might be reverted. Here's the relationship between shares (s) and assets (a) in the Pool:
• Share to Asset Conversion: a = [(s\*I + 10\^27 / 2) / 10\^27](rayMul)
```solidity
function rayMul(uint256 a, uint256 b) internal pure returns (uint256 c) {
    assembly {
        if iszero(or(iszero(b), iszero(gt(a, div(sub(not(0), HALF_RAY), b))))) {
            revert(0, 0)
        }
        c := div(add(mul(a, b), HALF_RAY), RAY)
    }
}
```
• Asset to Share Conversion: s = [(a\*10\^27 + I / 2) / I](rayDiv)
```solidity
function rayDiv(uint256 a, uint256 b) internal pure returns (uint256 c) {
    assembly {
        if or(iszero(b), iszero(iszero(gt(a, div(sub(not(0), div(b, 2)), RAY))))) {
            revert(0, 0)
        }
        c := div(add(mul(a, RAY), div(b, 2)), b)
    }
}
```
Numerical Example: Suppose there is a pool P where users borrow assets A using the NFTPositionManager.
• The current borrowindex of P is 2\*10\^27, and the share is 5.
• The previousDebtBalance is as below (Line119): previousDebtBalance = [(s\*I + 10\^27 / 2) / 10\^27] = [(5\*2\*10\^27 + 10\^27 / 2) / 10\^27] = 10
• If we are going to repay 3 assets:
  – The removed shares is: [(a\*10\^27 + I / 2) / I] = [(3\*10\^27 + 2\*10\^27 / 2) / (2\*10\^27)] = 2
  – Therefore, the remaining share is: 5 - 2 = 3
• The currentDebtBalance is as below (Line121): currentDebtBalance = [(s\*I + 10\^27 / 2) / 10\^27] = [(3\*2\*10\^27 + 10\^27 / 2) / 10\^27] = 6. Then in line123, previousDebtBalance - currentDebtBalance would be 4 and repaid.assets is 3. As a result, the repayment would be reverted.
```solidity
function _repay(AssetOperationParams memory params) internal nonReentrant {
    uint256 previousDebtBalance = pool.getDebt(params.asset, address(this), params.tokenId);
    DataTypes.SharesType memory repaid = pool.repay(params.asset, params.amount, params.tokenId, params.data);
    uint256 currentDebtBalance = pool.getDebt(params.asset, address(this), params.tokenId);
    if (previousDebtBalance - currentDebtBalance != repaid.assets) {
        revert NFTErrorsLib.BalanceMisMatch();
    }
}
```
This example demonstrates a potential 1 wei mismatch between previousDebtBalance and currentDebtBalance due to rounding in the calculations. This check seems to cause a denial-of-service(DoS) situation where repayments can fail due to small rounding errors. This issue can occur with various combinations of borrowindex, share amounts, and repaid assets.

## Recommendation
Either remove this check or adjust it to allow a 1 wei mismatch to prevent unnecessary reversion of repayments. Disclaimers project. Usage of all smart contract software is at the respective users’ sole risk and is the users’ responsibility.
