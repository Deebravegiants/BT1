# [M] HAM-1 | Uncapped Tax

## Summary
Severity: Medium
Contest weight: 0.0268
Dataset id: 8629
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an uncapped tax rate that can be set to as high as 99.99 percent through the contract’s setTaxRate function. The root cause is the absence of any upper‑bound validation or governance safeguard on the taxRate variable, allowing the privileged caller (typically the contract owner) to assign an arbitrarily large percentage. An attacker or a malicious administrator can exploit this by invoking setTaxRate with a value close to one hundred percent, after which every subsequent transfer or operation that applies the tax will deduct almost the entire amount from the sender. From a user’s perspective the expected outcome – for example receiving 90 % of a transferred amount after a modest fee – is replaced by a near‑total loss, often appearing as a zero or negligible balance in the UI with no explicit error. The impact is severe: users lose the majority of their funds, the protocol’s economic model is broken because the tax no longer reflects a reasonable fee, and trust in the platform is eroded. This condition occurs whenever the privileged function is called; there is no timelock, governance vote, or cap to prevent an abrupt change. The affected parties include token holders, liquidity providers, and any participant relying on the contract’s fee logic. The issue was discovered during a manual audit that highlighted the missing constraint on the taxRate parameter. It can be hard to notice because the contract may initially be deployed with a low tax, and the change can happen later without obvious on‑chain warnings. To remediate, the contract should enforce a strict maximum tax (for example 10 % or another business‑defined ceiling), optionally introduce a timelock or multi‑signature governance delay for tax updates, and emit clear events whenever the rate is altered so that observers can detect unexpected changes. This class of bug falls under “unbounded parameter control” and violates basic accounting assumptions that fees must be bounded and predictable.

## Recommendation
Require a more strict cap on the taxRate and/or timelock the setTaxRate function.
