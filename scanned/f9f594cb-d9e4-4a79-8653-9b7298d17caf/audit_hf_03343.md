# [M] GLOBAL-7 | Funding Fees Accumulate In Disabled Markets

## Summary
Severity: Medium
Contest weight: 0.0348
Dataset id: 18194
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an accounting flaw where funding fees continue to accrue even after the market’s trading functions (increase and decrease position) have been disabled. The root cause is that the fee‑accrual routine does not check the market’s enabled flag, so time‑based fee calculations run regardless of the market state. An attacker or any party with the ability to pause trading can let the market remain disabled while the protocol silently adds funding fees to every open position. When trading is later re‑enabled, the protocol automatically deducts the accumulated fees from traders’ balances, resulting in unexpected charges. This impacts any user who holds an open position during the disabled period, as well as the protocol itself because the unexpected fee deductions can erode user trust and distort accounting assumptions. The issue was discovered during a systematic audit of the market‑control logic, where the auditor noticed that the funding‑fee update function was called unconditionally in the time‑step loop. Because the fees are internal bookkeeping values, the problem may remain hidden from users until they attempt to trade again and see a larger-than‑expected fee or a reduced balance. From a user’s perspective the UI may show that trading is paused, yet after resumption the user sees a fee line they did not anticipate, or their balance appears lower than expected. The bug belongs to the class of “state‑inconsistent fee accrual” or “time‑based accounting when feature is disabled”. To remediate, the contract should gate the funding‑fee accumulation with the same enabled check used for position modifications, or explicitly pause the fee‑accrual mechanism when the market is disabled, ensuring that no fees are added while users cannot interact with the market. This aligns the protocol’s behavior with the business logic that fees should only be charged when trading activity is possible.

## Recommendation
Consider pausing funding fee accumulation when trading is disabled.
