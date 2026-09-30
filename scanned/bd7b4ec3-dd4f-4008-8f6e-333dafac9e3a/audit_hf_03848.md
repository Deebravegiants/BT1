# [M] When swapping 18-decimal token to 8-decimal

## Summary
Severity: Medium
Contest weight: 0.5305
Dataset id: 20100
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Here is the poc:
```solidity
uint256 payFromToken = d3Proxy.buyTokens(
    address(d3MM),
    user1,
    address(token1),
    address(token2),
    0,
    abi.encode(swapData),
    block.timestamp + 1000
);
assertEq(payFromToken, 0);
```
It may cause unexpected loss

## Recommendation
In buyToken() of D3Trading.sol, add this rule:
```solidity
if(payFromAmount == 0) { // value too small
    payFromAmount = 1;
}
```
