# [H] H-02 | closePosition May Break Through The Floor

## Summary
Severity: High
Contest weight: 0.0700
Dataset id: 21895
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the closePosition routine of the protocol, which is responsible for unwinding a leveraged position by swapping bAssets for reserve tokens and then re‑adding those reserves to the floor position. The function performs the asset swap before the floor position is updated, which creates a window where the market price of the sold bAsset can move the floor tick below the required minimum. When this happens the floor position is said to “break through” the floor tick, causing the internal accounting invariant that underpins the BLV token to be violated. The root cause is the ordering of operations: the contract assumes that adding the newly acquired reserves will always keep the floor tick intact, but it does not check the floor after the swap. An attacker or any user who triggers closePosition while the market price is unfavorable can cause the swap to consume more reserves than anticipated, pushing the floor below the safe threshold. The immediate impact is that the BLV token, which represents a claim on the floor position, may become invalid or redeemable for less than its expected value, effectively causing funds to disappear from users’ perspectives. This condition can occur whenever closePosition is called with a bAsset whose sale price is low enough to breach the floor, which may be rare but is possible under volatile market conditions. All participants who hold BLV or rely on the floor position for collateral are affected because the protocol’s safety net is compromised. The issue was discovered during a manual audit that examined the logical flow of the closePosition function and identified that the floor‑tick check present in the _deleverage path was missing here. The bug is subtle because the transaction does not revert; it appears to succeed, and the UI may still show a successful close, while the underlying floor invariant is silently broken, making the problem hard to notice without deep inspection of internal state. To remediate the issue the contract should perform a post‑swap verification of the floor tick and revert the transaction if the floor would be breached, mirroring the safeguard already present in the _deleverage routine. In broader terms this is a classic example of an accounting‑logic flaw where state updates are performed in an unsafe order, leading to a violation of financial invariants and potential loss of user funds.

## Recommendation
At the end of closePosition revert if _tradingInFloor is true, similar to in _deleverage.
