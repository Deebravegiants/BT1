# [M] BaseFlasher transfers tokens and then calls xBundle(...), so the sent tokens can't be returned due to the balance check

## Summary
Severity: Medium
Contest weight: 0.1249
Dataset id: 8224
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The BaseRouter checks if the balances of the assets remain the same after the xBundle(...) execution. The BaseFlasher, _requestorExecution(...) is implemented in the following way IERC20(asset).safeTransfer(requestor, amount); requestor.functionCall(requestorCalldata); // approve flashloan source address to spend to repay flashloan IERC20(asset).safeApprove(getFlashloanSourceAddr(asset), amount + fee); Thus, when xBundle(...) is called in requestor.functionCall(requestorCalldata);, the initial balance of the BaseRouter will take into account the received funds from the flashloan, such that it will be impossible to return the funds at the end of the call.

## Proof of Concept
no poc/POCCantUseFlashloanFunds.t.sol#L97/POCCantUseFlashloanFunds.t.sol#L97

## Recommendation
Similarly to xReceive(...) of the ConnextRouter, the BaseRouter could implement a similar function. In this case, the caller of, let's say, flashloanReceive(...), could be whitelisted to one of the flashers.
