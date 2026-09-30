# [M] Missing executor/clipperExchange check could result in malicious command

## Summary
Severity: Medium
Contest weight: 0.5516
Dataset id: 6070
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function swap(
    address executor,
    IGenericRouter.SwapDescription calldata desc,
    bytes calldata permit,
    bytes calldata data
) external payable override refundEth(desc.amount) returns (Command[] memory cmds_) {
    // ...
```
```solidity
function clipperSwapTo(
    address clipperExchange, // <== example of exchange param
    address payable recipient,
    Address srcToken,
    address dstToken,
    uint256 inputAmount,
    uint256 outputAmount,
    uint256 goodUntil,
    bytes32 r,
    bytes32 vs
) external payable override refundEth(inputAmount) returns (Command[] memory cmds) {
```
As we can see both are missing a check to ensure that that is a trustable executor which means that the command can be forged to use a malicious executor which could potentially siphon funds.

## Recommendation
Consider always checking these variables against known addresses, you could create a map which will whitelist executors that can be used.
