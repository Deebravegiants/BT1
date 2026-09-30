# [M] EDPU-3 | Market Token Price Below Allowed Amount

## Summary
Severity: Medium
Contest weight: 0.0648
Dataset id: 18203
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability concerns the deposit gating logic of a synthetic market that uses a constant called MAX_PNL_FACTOR_FOR_DEPOSITS to decide whether new deposits are allowed. The contract assumes that the market token price will never fall below a certain “allowed” amount, and it only blocks deposits when the PnL factor exceeds the maximum. In practice, after an Auto‑Deleveraging (ADL) event the market token price can keep decreasing, potentially dropping below the assumed minimum. Because the deposit check does not re‑evaluate the absolute price floor, the system may incorrectly permit deposits even though the price is lower than intended. An attacker can trigger or wait for an ADL, observe the price sliding further down, and then submit a deposit transaction that passes the MAX_PNL_FACTOR_FOR_DEPOSITS test. By depositing at a price that is artificially low, the attacker can obtain a larger position for the same amount of collateral, effectively extracting value from the protocol or causing other users’ positions to be under‑collateralized. The impact is a distortion of accounting: the protocol’s accounting assumptions about token value are violated, leading to potential loss of funds, unfair advantage for the depositor, and erosion of trust in the market’s pricing guarantees. This condition occurs only after an ADL event when the price can continue to drift downward; under normal market conditions the price floor assumption may hold, which is why the bug can be subtle and easy to miss. The issue was discovered during a formal audit where test cases demonstrated that deposits resumed after the price fell below the allowed threshold. It is hard to notice because the contract does not emit explicit warnings when the price breaches the assumed minimum, and the existing check appears to work correctly for most scenarios. To remediate, the contract should not rely on a static minimum price bound. Instead, the deposit logic must either enforce a dynamic price floor that is continuously validated after ADL or incorporate the actual market token price into the gating condition. Documentation should also be updated to state that the price may drop below the previously asserted “allowed” amount, and any business logic that depends on that assumption must be revised. In summary, the bug is a price‑floor assumption flaw that allows deposits when the market token price is lower than expected, breaking the protocol’s accounting model and potentially leading to fund loss or unfair position sizing.

## Proof of Concept
https://github.com/GuardianAudits/GMX_3/blob/main/test/Guardian/PoCs/EDPU_3.ts

## Recommendation
Do not count on this minimum bound for market token price and be sure to document that the price can keep dropping below the asserted “allowed” amount.
