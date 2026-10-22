# [C] UBT-1 | Treasury Cannot Receive ETH

## Summary
Severity: Critical
Contest weight: 0.0555
Dataset id: 16240
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is that the treasury contract does not implement a receive() or fallback() function marked payable, which means the contract is unable to accept plain Ether transfers. The root cause is the omission of a payable entry point for the contract, so any transaction that sends ETH without calling a specific payable function triggers the default behavior of rejecting the transfer and reverting. An attacker or any legitimate user who attempts to fund the treasury by sending ETH directly, or by relying on a fee‑forwarding mechanism, will see the transaction fail or the Ether become permanently locked in the sending address. The impact is that protocol fees, rewards, or any other Ether intended for the treasury never arrive, leading to missing balances, zero refunds, and potentially halted economic flows. This condition occurs whenever the contract receives a plain value transfer, which is common in DeFi protocols that forward fees automatically. All participants who expect the treasury to hold Ether—users, liquidity providers, and the protocol itself—are affected because the accounting assumptions that the treasury will increase its balance are violated. The issue was discovered during a manual audit that inspected the contract’s external interface and noticed the absence of a receive or fallback payable function. Because the contract compiles without errors and the missing function does not raise a warning, the problem can be easy to overlook, especially if tests only call named functions. The bug belongs to the class of “missing payable fallback” or “inability to receive Ether” vulnerabilities, which break the invariant that a contract can accept Ether sent via the transfer or call methods. From a user’s perspective the UI may show a successful transaction hash while the treasury balance remains unchanged, or the user may receive a revert message stating that the contract does not accept Ether. Users expect their fees to be deposited and later redistributed, but instead the funds stay with the sender or are reverted, effectively causing “funds disappear” or “refund calculation error”. To remediate the issue the contract should be extended with a receive() external payable {} function (or a payable fallback()) so that any plain Ether transfer is accepted and correctly recorded in the treasury’s balance. Adding this entry point restores the intended accounting flow and prevents Ether from being unintentionally rejected.

## Recommendation
Add a receive() external payable { } function to the contract.
