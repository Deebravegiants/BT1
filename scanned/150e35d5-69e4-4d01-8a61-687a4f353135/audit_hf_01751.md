# [M] M-1 Rounding errors

## Summary
Severity: Medium
Contest weight: 0.0401
Dataset id: 9561
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a rounding error that occurs in the L2 ERC20RebasableBridged contract when converting between stETH shares and the wrapped representation on Optimism. Because the contract uses integer division without proper rounding, a small remainder – often referred to as dust – is left in the user's balance after an unwrap or bridge operation. The root cause is the loss of precision when the rebasing token amount is scaled to the fixed‑point representation required for the L2 bridge, causing the fractional part to be truncated. An attacker does not gain direct control over this dust, but any user who performs the conversion will end up with a non‑zero balance that cannot be withdrawn through the existing interface, leading to a discrepancy between the expected refund amount and the actual amount received. This situation manifests when a user unwraps stETH to wstETH or when the bridge settles a transfer; the UI may display a zero balance because the remaining amount is below the displayed precision, while the on‑chain balance still contains a few wei. The issue was discovered during a manual audit by MixBytes, which identified that the code paths at lines 86‑94 always leave a remainder due to the rounding logic. The problem is hard to notice because the dust is typically very small and may be rounded to zero in front‑end displays, giving the impression that the operation succeeded fully. The impact is primarily financial – users lose the ability to claim the leftover tokens, which over many operations can accumulate to a noticeable loss – and it violates the protocol’s accounting assumption that all transferred value is fully accounted for after a bridge operation. The recommended mitigation is to add a dedicated method that allows users to convert the remaining stETH shares into wstETH shares, effectively enabling them to claim the dust, or to adjust the arithmetic to use rounding up or a higher precision representation so that no remainder is left.

## Recommendation
We recommend adding a method that allows users to unwrap stETH shares into wstETH shares.
