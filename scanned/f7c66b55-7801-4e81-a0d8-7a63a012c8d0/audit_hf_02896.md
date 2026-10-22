# [H] MS-1 | Principal Admin Abuse

## Summary
Severity: High
Contest weight: 0.0842
Dataset id: 16197
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of an unchecked ability for the principal admin to call the function that registers new approver addresses, allowing the admin to add as many addresses as needed to satisfy the quorum required for transaction approval. The root cause is the lack of proper access control and quorum enforcement on the setApproverAddr routine; the contract does not require existing approvers to consent to the addition of new ones, nor does it limit the number of addresses that can be added by a single privileged account. An attacker who controls the principal admin can therefore create a set of approvers that are all under their control, reach the quorum threshold, and approve any arbitrary treasury transaction without any independent verification. This defeats the intended multi‑signature security model, turning what should be a decentralized decision process into a single‑point‑of‑failure. The impact is that funds can be moved out of the treasury without the consent of other admins or the community, leading to potential theft, loss of trust, and violation of the protocol’s governance assumptions. The condition under which this occurs is any time the principal admin invokes setApproverAddr, which can be done repeatedly and at will. All participants who rely on the multi‑sig guarantee—token holders, users, and the protocol itself—are affected because the treasury’s safety is compromised. The issue was discovered during a manual audit that examined the governance flow and identified that the admin could manipulate the approver list without restriction. It may be hard to notice because the function appears benign, simply adding addresses, and the contract does not emit warnings or checks that the added addresses are distinct or that a majority of existing admins have approved the change. To remediate, the contract should enforce that any addition or removal of an approver requires approval from a majority of the current approvers, enforce a reasonable limit on the total number of approvers, and ensure that the quorum cannot be satisfied by addresses controlled by a single admin, thereby restoring a true multi‑signature governance model.

## Recommendation
Make it so a majority of admins must agree to add or remove another admin or partake in other
important decisions with the treasury.
