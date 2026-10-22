# [M] Should use >= instead of >

## Summary
Severity: Medium
Contest weight: 0.1435
Dataset id: 15809
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The comparison should be `a >= vlt.notional` instead of `a > vlt.notional`.

Otherwise dust amounts will always be left in `vlt.notional` when calling `removeNotional()` or `transferNotionalFrom()`.

While the leakage is potentially … 1 wei, its leakage nonetheless and a frontend would surely provide the max amount most of the time leading to reverts.
 
Maybe a quick severity review from wardens but happy with where its at.

I agree that this is quite low stakes, given that there is non-zero potential leakage I think the warden should get credit for this as a Medium Risk vulnerability. Per the C4 juging criteria:

> 2 — Med: Assets not at direct risk, but the function of the protocol or its availability could be impacted, or leak value with a hypothetical attack path with stated assumptions, but external requirements.

**[robrobbins (Swivel) resolved](https://github.com/code-423n4/2022-07-swivel-findings/issues/21#issuecomment-1211292178):**

Addressed: <https://github.com/Swivel-Finance/gost/pull/423>.

## Recommendation
No recommendation
