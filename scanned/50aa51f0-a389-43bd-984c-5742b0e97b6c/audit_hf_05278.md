# [M] Changing stablecoin on TokenBank can mess up fees collection

## Summary
Severity: Medium
Contest weight: 0.0000
Dataset id: 23509
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The feeAmount on each token is computed with the decimals of the current stablecoin (initially, a stablecoin of 6 decimals). If the stablecoin is changed to another one that uses decimals != than 6, if there are any pending fees before changing the stablecoin, those pending fees will then be paid with the new stablecoin, causing the actual collected money to be different than expected.  
It is possible that by normal operations, a tx to buyTokens gets executed in between fees were claimed and the stablecoin is changed, if the purchased of new tokens generates fees, those new fees will be computed based on the current stablecoin, but will be paid out in the new stablecoin. For example: if 10USDC (10e6) are as pending fees, and the new stablecoin is USDT (10e8), when those fees are collected, they will represent 0.1USDT.

```solidity
function buyToken(
    address tokenAddress,
    uint32 amount
) external nonReentrant {
    ...
    uint64 feeValue = (stablecoinValue * curData.saleFee) / 1e6;
    ...
    curData.feeAmount += feeValue;
    IERC20(stablecoin).transferFrom(
        to,
        address(this),
        stablecoinValue + feeValue
    );
    ...
}
```

```solidity
function claimAllFees() external nonReentrant restricted {
    ...
    for (uint i = 0; i < developments.length; ++i) {
        //@audit => Pending fees before stablecoin was changed were computed with the decimals of the old
        stablecoin,!
        totalValue += tokenData[developments[i]].feeAmount;
        tokenData[developments[i]].feeAmount = 0;
    }
    IERC20(stablecoin).transfer(custodialWallet, totalValue);
}
```

Impact: Collected fees can be different from expected if the stablecoin is changed to a stablecoin that has different decimals than 6.

## Recommendation
Similar to how values are normalized to the decimals of the current stablecoin on the PledgeManager, implement the same logic on the TokenBank.  

- Normalize the amounts of stablecoin before doing the actual transfers.

```solidity
function claimAllFees() external nonReentrant restricted {
    ...
    - IERC20(stablecoin).transfer(custodialWallet, totalValue);
    + IERC20(stablecoin).transfer(custodialWallet, _fixDecimals(totalValue));
    ...
}
```

```solidity
//@audit => Add this function to normalize values to decimals of the current stablecoin
function _fixDecimals(uint256 value) internal view returns (uint256) {
    return
        stablecoinDecimals < 6
            ? value / (10 ** (6 - stablecoinDecimals))
            : value * (10 ** (stablecoinDecimals - 6));
}
```
