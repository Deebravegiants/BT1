# [C] C-1 Debug code in getPriceByExternal

## Summary
Severity: Critical
Contest weight: 0.0773
Dataset id: 7523
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of a hard‑coded return value left in the price‑retrieval routine of a betting protocol. The function that is supposed to query an external price oracle ends with an unconditional return of the constant 30_000e18 (and a zero second value). Because the function never forwards the oracle’s actual data, every settlement that relies on this price uses the same fixed figure. The root cause is debug or placeholder code that was not removed before deployment. An attacker can trigger the settlement logic with a known price, predict the outcome of the bet, and place opposing positions to guarantee a profit, since the protocol will calculate winnings based on the fabricated constant instead of the real market price. The impact is that users receive incorrect payouts: some may lose funds they should have won, while the attacker gains the difference. The bug manifests whenever the contract calls the price‑retrieval function, i.e., during every battle settlement, regardless of the external market conditions. All participants in the betting system are potentially affected, but the attacker benefits the most. The issue was uncovered during a manual security audit that inspected the oracle integration and noticed the final line returning a static value. Because the function signature appears legitimate and the constant value is large, the problem can be subtle and may not be obvious from high‑level testing that only checks that a price is returned. The bug violates the core accounting assumption that settlement amounts are derived from up‑to‑date oracle data, breaking the economic model of the protocol. To remediate, the constant return statement should be removed and the function must forward the actual price obtained from the external oracle, with appropriate checks for freshness and validity. After correction, settlements will reflect true market prices, restoring expected user behavior where a bettor receives a payout proportional to the real price rather than a fixed, erroneous amount.

## Recommendation
We recommend removing the return (30_000e18, 0) instruction from the function.
