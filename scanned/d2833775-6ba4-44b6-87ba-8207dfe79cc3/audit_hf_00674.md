# [M] M-01 | Missing Equality Operator

## Summary
Severity: Medium
Contest weight: 0.0402
Dataset id: 2210
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an off‑by‑one logic error in the price‑floor validation performed by the router contract. The contract is supposed to reject a trade when the current market tick (activeTick) is at or above the upper bound of a predefined floor (tickU). In the reference implementation the check uses a less‑than‑or‑equal operator (activeTick <= tickU) which correctly blocks trades that would violate the floor price. In the router, however, the comparison uses only a strict less‑than operator (activeTick < tickU). As a result, when activeTick is exactly equal to tickU the condition evaluates to true and the trade is allowed to proceed. The root cause is the missing equality part of the comparison, a classic off‑by‑one mistake. An attacker or any user can exploit this by submitting a trade that is timed to hit the exact floor tick; the contract will not revert and will execute the trade at a price that the protocol intended to forbid. This can lead to users receiving a worse price than expected, liquidity providers losing value, and the overall economic model of the protocol being compromised because the floor‑price guarantee is broken. The issue manifests only when the market tick matches the floor’s upper tick, a situation that can occur naturally as prices move. It affects all participants who rely on the floor protection, including traders, liquidity providers, and the protocol itself. The bug was discovered during a manual audit that compared the router’s logic with the policy contract and noticed the discrepancy in the comparison operator. Because the difference is a single character, it can be easily overlooked in code reviews and testing, especially when the surrounding logic appears correct. From a user’s perspective the symptom is that a trade that should have been rejected executes, often resulting in an unexpected loss or a balance that appears to have been reduced without a clear error message. The bug belongs to the class of boundary‑condition errors where an equality check is omitted, leading to unintended state transitions. To remediate the issue the comparison should be changed to a less‑than‑or‑equal operator, ensuring that the contract reverts whenever activeTick is exactly at the floor limit, thereby restoring the intended floor‑price protection.

## Recommendation
Update the operator to <= so the call reverts when active tick is exactly at the BLV.
