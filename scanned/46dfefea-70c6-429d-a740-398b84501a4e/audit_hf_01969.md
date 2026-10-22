# [H] .transfer() fails for non standard ERC20s such as USDT and gets stuck

## Summary
Severity: High
Contest weight: 0.0714
Dataset id: 11106
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability arises from the contract’s use of the standard IERC20 interface to invoke the transfer function when sending tokens to a caller. The ERC20 specification defines transfer as returning a boolean indicating success, and the OpenZeppelin IERC20 abstraction includes a check that the call returns at least 32 bytes. Some widely deployed tokens, most notably USDT, deviate from the spec and implement transfer without returning any data. When the contract executes IERC20(tkn).transfer(msg.sender, amount) against such a token, the EVM’s built‑in return‑data size verification fails, causing the call to revert. As a result, the intended token transfer never occurs and the tokens remain locked inside the contract. Users attempting to withdraw see no change in their wallet balance; the front‑end may incorrectly report success because the transaction receipt is not examined for the revert reason. The issue manifests whenever a user requests a withdrawal of a non‑standard ERC20 token, or any internal logic that relies on transfer returning a value. It affects any participant who holds the affected token and interacts with the contract, including regular users, liquidity providers, and the protocol itself, because the stuck funds reduce available liquidity and can break accounting assumptions. The problem was identified during a manual code review where the auditor noted a direct call to IERC20.transfer and confirmed the failure by testing with USDT. Because the revert occurs at the low‑level call level, it may be difficult to notice without explicit transaction status checks or testing against non‑standard tokens. The bug belongs to the class of “ERC20 incompatibility” or “missing return value” errors, where contracts assume compliance with the ERC20 interface but interact with tokens that do not follow it. The correct mitigation is to replace raw transfer calls with OpenZeppelin’s SafeERC20.safeTransfer, which internally handles missing return data by using low‑level calls and checking success via the optional return‑value pattern. By doing so, the contract can safely transfer both standard and non‑standard tokens, preventing funds from becoming irretrievable.

## Recommendation
Use safeTransfer() from Openzeppelin's `SafeERC20`.
