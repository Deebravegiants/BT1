# [M] Code credits fee-on-transfer tokens for amount stated, not amount transferred

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-07-juicebox
Published: 2022-07-08
Source: https://github.com/code-423n4/2022-07-juicebox-findings/issues/304
Type: code-finding

## Details
# Lines of code

https://github.com/jbx-protocol/juice-contracts-v2-code4rena/blob/828bf2f3e719873daa08081cfa0d0a6deaa5ace5/contracts/abstract/JBPayoutRedemptionPaymentTerminal.sol#L817-L856


# Vulnerability details

Some ERC20 tokens, such as USDT, allow for charging a fee any time `transfer()` or `transferFrom()` is called. If a contract does not allow for amounts to change after transfers, subsequent transfer operations based on the original amount will `revert()` due to the contract having an insufficient balance. 


## Impact
If there is only one user that has use a payment terminal with a fee-on-transfer token to pay a project for its token, that project will be unable to withdraw their funds, because the amount available will be less than the amount stated during deposit, and therefore the token's `transfer()` call will revert during withdrawal. For more users, consider what happens if the token has a 10% fee-on-transfer fee - deposits will be underfunded by 10%, and the projects trying to withdraw the last 10% of deposits/rewards will have their calls revert due to the contract not holding enough tokens. If a whale does a large withdrawal, the extra 10% that that whale gets will mean that _many_ projects will not be able to withdraw anything at all.

## Proof of Concept
Because the terminals rely on terminal stores, which only store the initial value provided during the payment, and provide it during distributions, the terminals are unable to use the decreased value when they later are told to distribute funds to a project. 

`JBSingleTokenPaymentTerminalStore.recordPaymentFrom()` stores the value passed in:
```solidity
File: contracts/JBSingleTokenPaymentTerminalStore.sol   #1

372       // Add the amount to the token balance of the project.
373       balanceOf[IJBSingleTokenPaymentTerminal(msg.sender)][_projectId] =
374         balanceOf[IJBSingleTokenPaymentTerminal(msg.sender)][_projectId] +
375         _amount.value;
```
https://github.com/jbx-protocol/juice-contracts-v2-code4rena/blob/828bf2f3e719873daa08081cfa0d0a6deaa5ace5/contracts/JBSingleTokenPaymentTerminalStore.sol#L372-L375


And provide that same value when recording a dispersion:
```solidity
File: contracts/JBSingleTokenPaymentTerminalStore.sol   #2

597       // Removed the distributed funds from the project's token balance.
598       balanceOf[IJBSingleTokenPaymentTerminal(msg.sender)][_projectId] =
599         balanceOf[IJBSingleTokenPaymentTerminal(msg.sender)][_projectId] -
600         distributedAmount;
```
https://github.com/jbx-protocol/juice-contracts-v2-code4rena/blob/828bf2f3e719873daa08081cfa0d0a6deaa5ace5/contracts/JBSingleTokenPaymentTerminalStore.sol#L597-L600

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-07-juicebox-findings/issues/304_
