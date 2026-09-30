# [M] DIEMT-3 | Errant Fee Applied

## Summary
Severity: Medium
Contest weight: 0.0428
Dataset id: 99
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of an incorrect settlement‑fee calculation that charges a fee on the premium regardless of whether the trade resulted in a profit or a loss. The contract determines the fee amount using the constant FEE_TAKEN_PROFITS and applies it directly to the premium before the profit‑and‑loss (PnL) for the position is calculated. For buy‑side (isBuy) positions the premium represents a potential profit, so the fee is effectively taken from genuine earnings. However, for sell‑side ( !isBuy ) positions the premium is actually a loss; the contract still subtracts the fee from this amount, turning a negative PnL into an even larger negative value. The root cause is that the fee is computed prior to PnL resolution and is not conditioned on the sign of the resulting profit. An attacker or any market participant can exploit this by opening sell‑side positions, knowing that the protocol will deduct the fee even when the trade ends in a loss, thereby increasing the user’s net loss. The impact is financial: users receive less than expected refunds or payouts, see balances reduced more than market movements dictate, and may perceive that the protocol unfairly siphons funds. The issue manifests whenever a position settles with a loss, i.e., when the underlying price moves against the trader’s direction. All participants who trade on the affected contract are affected, but primarily those on the sell side. The flaw was discovered during a systematic audit of settlement logic, where the flow of fee calculation was traced and found to be decoupled from profit determination. It can be hard to notice because the fee amount appears constant and the transaction receipts do not obviously reveal that the fee is being taken from a loss rather than a profit, especially when users only see the final net amount. To remediate, the fee should be applied only after the PnL is known and only when the result is positive; if the PnL is negative, the fee must be waived or computed on the absolute profit value after the loss is accounted for. In abstract terms, this is a misapplied accounting rule where a charge is levied on a negative balance, violating the expectation that fees are taken from earned value, not from losses, and breaking the contract’s economic guarantees.

## Recommendation
Do not fee this amount if it represents a loss, additionally compute the fee after the PNL has been determined, this way true profits are feed with the FEE_TAKEN_PROFITS amount.
