# [M] M-1 Incorrect event emitting

## Summary
Severity: Medium
Contest weight: 0.0176
Dataset id: 7985
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an incorrect event emission in the NFT minting routine. During a batch mint operation the contract updates the internal ownership mapping with the correct token identifier calculated as the base tokenId plus the loop index (tokenId + i). However, the emitted Mint event logs only the base tokenId or an otherwise wrong identifier, omitting the +i offset. This discrepancy originates from a simple coding mistake where the variable used in the emit statement does not match the value actually assigned to the newly minted token. Because the contract’s state changes are correct, the error is not visible on‑chain through balance queries, but external observers that rely on events – such as wallets, marketplaces, analytics dashboards, or royalty distribution scripts – will record an inaccurate tokenId. Consequently a user may see a Mint event indicating they received token X while the contract actually assigned token X+1, leading to confusion, potential mis‑routing of royalties, or failed look‑ups in off‑chain services. The issue manifests whenever the batch mint function is called, i.e., when more than one token is minted in a single transaction. All participants that depend on event data – token owners, third‑party services, auditors, and protocol developers – are affected because the emitted data no longer reflects the true on‑chain state. The flaw was discovered during a manual security audit performed by MixBytes, which compared the logic of the mint loop with the emitted parameters and noticed the mismatch. It can be hard to notice because typical unit tests focus on state changes and may not assert the exact values of emitted events, especially in loops where the expected values are dynamic. To remediate the problem the contract should emit the exact token identifier used for assignment, i.e., emit Mint(_to, tokenId + i);, ensuring that the event data aligns with the internal state and that downstream systems receive accurate information. This class of bug falls under “event mismatch” or “incorrect logging” where emitted data does not faithfully represent the executed logic, violating the accounting assumption that events are a reliable source of truth for external observers.

## Recommendation
We recommend changing the event to the emit Mint(_to, tokenId + i);.
