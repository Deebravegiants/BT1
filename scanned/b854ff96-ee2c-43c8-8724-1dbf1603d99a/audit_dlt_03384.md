# [M] Transaction-Order-Dependence race condition for approveTransferERC20()

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-05-visorfinance
Published: 2021-05-19
Source: https://github.com/code-423n4/2021-05-visorfinance-findings/issues/33
Type: code-finding

## Details
# Handle

0xRajeev


# Vulnerability details

## Impact

Similar to ERC20 approve() being susceptible to double-spend allowance due to front-running, approveTransferERC20() here is also susceptible. For reference, see https://swcregistry.io/docs/SWC-114.

This is the classic ERC20 approve() race condition where a malicious spender can double-spend allowance (old and new allowance) by front-running the owner’s second approve() call that aims to change the allowance.

The impact is double-spend of approved tokens which leads to loss of owner’s funds when owner tries to change spender’s allowance.

## Proof of Concept

Assume that Alice has approved Eve to transfer n of her tokens, then Alice decides to change Eve's approval to m tokens. Alice submits a function call to approve with the value m for Eve. Eve monitors the Ethereum mempool and so knows that Alice is going to change her approval to m. Eve immediately submits a transferFrom request sending n of Alice's tokens to herself, but gives it a much higher gas price than Alice's transaction to front-run it. The transferFrom executes first so gives Eve n tokens and sets Eve's approval to zero. Then Alice's transaction executes and sets Eve's approval to m tokens. Eve then sends those m tokens to herself as well. Thus Eve gets n + m tokens even thought she should have gotten at most max(n,m).

Expected order where Eve can only transfer 50 tokens:
1. Alice: approveTransferERC20(token, Eve, 100)
2. Alice: approveTransferERC20(token, Eve, 50)
3. Eve: delegatedTransferERC20(token, Eve, 100) -> Fails
4. Eve: delegatedTransferERC20(token, Eve, 50) -> Passes

Exploit order where Eve can transfer 150 tokens:
1. Alice: approveTransferERC20(token, Eve, 100)
2. Eve: delegatedTransferERC20(token, Eve, 100) -> Passes
3. Alice: approveTransferERC20(token, Eve, 50)
4. Eve: delegatedTransferERC20(token, Eve, 50) -> Passes


https://github.com/code-423n4/2021-05-visorfinance/blob/e0f15162a017130aa66910d46c70ee074b64dd40/contracts/contracts/visor/Visor.sol#L426-L432

https://github.com/code-423n4/2021-05-visorfinance/blob/e0f15162a017130aa66910d46c70ee074b64dd40/contracts/contracts/visor/Visor.sol#L434-L463


## Tools Used

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2021-05-visorfinance-findings/issues/33_
