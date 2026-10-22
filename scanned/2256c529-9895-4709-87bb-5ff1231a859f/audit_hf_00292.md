# [M] Check _to is not empty

## Summary
Severity: Medium
Contest weight: 0.0340
Dataset id: 1470
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability originates from three contract functions—claimYield, _withdraw, and _unsponsor—that accept an external address parameter called _to but do not verify that the supplied address is non‑zero. Because the code lacks a require(_to != address(0)) guard, an attacker or a careless user can intentionally or unintentionally pass the null address (0x0000000000000000000000000000000000000000) as the destination for transferred assets. When the contract attempts to send tokens, ETH, or any other value to this address, the transfer succeeds but the funds are effectively burned, removing them permanently from the protocol's balance sheet. The exploit can be triggered whenever a caller is able to invoke any of the three functions with a custom _to argument; no additional conditions are required beyond the function’s normal access controls. From the user’s perspective the symptom is a missing payout: a user who expects to receive a yield, a withdrawal, or a sponsor refund instead sees a zero balance or receives no tokens, often without an explicit error message. The impact is a loss of funds for the affected user and a reduction of the protocol’s total assets, potentially breaking accounting assumptions such as total supply, sponsor balances, or yield distribution totals. This issue was uncovered during a Code4rena audit when reviewers noted the absence of an empty‑address check, a common defensive pattern in Solidity contracts. The problem can be hard to notice because a zero‑address transfer does not revert and the UI may simply show a successful transaction with no visible indication that the assets have been destroyed. The recommended mitigation is to add explicit validation that the _to argument is not the zero address before any transfer logic is executed, thereby preventing accidental burns and preserving expected financial flows. In broader terms the bug belongs to the class of missing input validation or unchecked address parameters, which can lead to unintended asset loss and violate core business logic that assumes funds are always transferred to a legitimate recipient.

## Recommendation
Consider implementing the proposed validation: require `_to != address(0)`

In this case assets are at risk due to external factors. A zero address check makes sense.
