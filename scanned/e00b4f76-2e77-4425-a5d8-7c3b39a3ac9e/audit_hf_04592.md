# [M] M-25 | mint In Fraxlend Rounds In Users’ Favour

## Summary
Severity: Medium
Contest weight: 0.0231
Dataset id: 22196
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a rounding bias in the mint function of the FraxlendPairCore contract. When a user calls mint to receive protocol shares in exchange for depositing assets, the contract calculates the number of shares by dividing the deposited amount by the current share price and then applies integer division that rounds down. Because the rounding is performed in favour of the user, the user receives slightly more shares than the exact proportional value would dictate, effectively paying fewer assets for the same amount of shares. The root cause is the use of floor division without a compensating safety margin, which is a classic arithmetic rounding error. An attacker can exploit this by repeatedly minting small amounts, where the rounding error per transaction is tiny but accumulates, allowing the attacker to acquire a larger share of the pool for less collateral. The impact is a gradual dilution of existing shareholders, a reduction in the total asset backing per share, and potential insolvency of the lending pool if the bug is exercised at scale. The condition under which it occurs is any call to the mint function that involves a division operation; the effect is more pronounced with small deposit amounts but is present for all minting actions. All participants in the Fraxlend protocol—depositors, borrowers, and token holders—are affected because the protocol’s accounting assumptions that each share is fully backed become violated. The issue was discovered during a manual audit that compared the expected proportional minting logic with the actual implementation and noticed that the rounding direction favoured users. Because the per‑transaction discrepancy is often only a few wei, it can be difficult to notice in normal operation, especially when users only see that they receive the expected number of shares. The bug belongs to the class of rounding‑bias or arithmetic‑precision vulnerabilities that break financial invariants. To fix the problem the mint calculation should be changed to round up (ceil) or to include a small protocol‑level buffer so that the protocol never receives fewer assets than required for the minted shares. In user‑facing terms, a user may observe that after minting they receive more shares than anticipated while the pool’s total assets appear slightly lower than expected, leading to a situation where funds disappear from the protocol’s perspective even though individual users seem to get a better deal.

## Recommendation
Round-up in favour of the protocol.
