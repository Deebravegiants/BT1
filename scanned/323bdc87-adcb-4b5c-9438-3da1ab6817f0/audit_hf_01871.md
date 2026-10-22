# [M] M-8 Centralization risks

## Summary
Severity: Medium
Contest weight: 0.0363
Dataset id: 10404
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a centralization risk that allows a privileged receiver to front‑run the creation of a new escrow and modify the fee parameters immediately before the escrow contract is instantiated. The root cause is that the fee‑update function in the escrow factory contracts is callable by a single address without any time‑lock or multi‑step governance, meaning the fee can be changed in the same block as a pending escrow creation transaction. An attacker who monitors the mempool can see a user’s transaction that will create an escrow with a certain fee, then submit a transaction that changes the fee to a higher value before the factory processes the escrow creation. Because the factory reads the fee value at the moment of escrow deployment, the newly created escrow records the malicious fee, causing the user to pay more than expected or, in extreme cases, to lose funds if the fee is set to an amount that drains the escrow balance. This exploit occurs whenever fee updates are unrestricted and can be executed in the same block as escrow creation, affecting any user attempting to lock assets, the protocol’s reputation, and any token holders relying on fair fee calculation. The issue was discovered during a manual audit of the factory contracts, where the auditor noted that the fee‑changing function was not protected by a delay or governance process and could be invoked by the same address that receives the fees. The problem is subtle because fee changes are legitimate operations and may not raise alarms; the malicious transaction blends with normal fee‑update activity, making it hard to detect without analyzing transaction ordering. To remediate, the fee update should be split into a two‑step process with a mandatory time delay, or restricted to a decentralized governance mechanism, ensuring that any fee change is visible to users before it can affect escrow creation. This would align the contract’s behavior with the expected business logic that fees are predictable and cannot be arbitrarily altered at the moment of escrow deployment, thereby preventing users from experiencing unexpected higher fees, missing refunds, or loss of locked assets.

## Recommendation
We recommend using a 2-step fee update with a mandatory time delay to mitigate this risk, ensuring transparency in fee adjustments.
