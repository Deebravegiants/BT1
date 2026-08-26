# [?] fix: Reject ERC-1155 batch transfers whose aggregate quantity overflows

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2026-05-12
Source: https://github.com/LedgerHQ/app-ethereum/commit/2f24a04bcfa6d4faf0b455d19a59ff10bb380c51
Type: security-commit

## Details
fix: Reject ERC-1155 batch transfers whose aggregate quantity overflows

The ERC-1155 batch_transfer parser accumulates per-id values into
context->value via add256() to compute the total quantity displayed
on the review screen. add256 wraps on uint256 overflow without
signalling, so a crafted calldata whose values sum past 2^256 would
silently produce a truncated total - a hostile dApp could pair a
benign-looking aggregate with adversarial per-id quantities.

After each accumulation, detect overflow by checking
gt256(&new_value, &context->value): when the running total is now
smaller than the addend, the sum has wrapped. Set the plugin result
to ERROR so the host cannot present a misleading review screen.
