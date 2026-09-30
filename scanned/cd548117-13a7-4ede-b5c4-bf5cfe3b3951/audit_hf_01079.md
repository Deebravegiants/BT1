# [M] Not calling `approve

## Summary
Severity: Medium
Contest weight: 0.5657
Dataset id: 4135
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Some tokens do not implement the ERC20 standard properly but are still accepted by most code that accepts ERC20 tokens. For example Tether (USDT)‘s `approve()` function will revert if the current approval is not zero, to protect against front-running changes of approvals.

## Proof of Concept
1. File: contracts/vault_and_oracles/FlashLoan.sol (line 48)
```solidity
IERC20(assets[0]).approve(address(LP_VAULT), amounts[0]);
```
2. File: contracts/vault_and_oracles/FlashLoan.sol (line 58)
```solidity
IERC20(assets[0]).approve(address(LENDING_POOL), amountOwing);
```
3. File: contracts/vault_and_oracles/UniV3LpVault.sol (line 418)
```solidity
IERC20Detailed(params.asset).approve(msg.sender, owedBack);
```
There are other calls to `approve()`, but they correctly set the approval to zero after the transfer is done, so that the next approval can go through.

## Recommendation
Use OpenZeppelin’s `SafeERC20`’s `safeTransfer()` instead.

Agree that we should set approve 0 before all approvals to avoid approval protection reverting and to support assets such as USDT.

**[0xdramaone (Duality Focus) resolved](https://github.com/code-423n4/2022-04-dualityfocus-findings/issues/39)**
