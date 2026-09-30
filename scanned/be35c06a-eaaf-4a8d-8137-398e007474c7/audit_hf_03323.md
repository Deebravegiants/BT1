# [H] GLOBAL-5 | Reference Exchange Manipulation

## Summary
Severity: High
Contest weight: 0.0647
Dataset id: 18174
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an oracle manipulation risk that stems from the way the protocol derives its reference price. The system collects price data from a limited set of external exchanges and computes the median value, which is then used to price synthetic assets and to trigger liquidations. Because the aggregation relies on a small number of sources, an attacker who can trade a sufficiently large volume on one or more of those reference exchanges can push the reported price away from the true market level. By creating an outlier price that moves the median, the attacker can cause the protocol to believe that the synthetic asset price has moved, allowing the attacker to open or close positions at a favorable rate, trigger liquidations of honest users, or extract value from the system. The issue occurs when the number of reference exchanges is low, when open‑interest caps are generous, and when the attacker possesses enough capital to influence the price on a reference exchange. Users experience symptoms such as unexpected liquidations, sudden drops in their balances, or receiving a refund that is far lower than expected, even though the broader market appears stable. The problem was identified during a security audit that examined the oracle design and recognized that the median calculation does not provide sufficient resistance to price outliers. The flaw is hard to notice because price deviations can be mistaken for normal market volatility, and the median may still look plausible while being subtly shifted. To remediate the issue, the protocol should increase the diversity and number of reference exchanges, apply more robust aggregation methods such as trimmed means or weighted medians, enforce tighter open‑interest limits, and add sanity checks that compare the median against broader market indicators. These measures reduce the influence any single exchange can have on the price feed, restoring confidence that the pricing logic aligns with the intended economic assumptions of the synthetic market.

## Recommendation
Carefully monitor the protocol and adjust parameters such as OI caps accordingly. Furthermore, use enough reference exchanges so the median is less likely to be affected by price outliers.
