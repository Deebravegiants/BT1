# [H] MJR-1 Invalid owner of token

## Summary
Severity: High
Contest weight: 0.0181
Dataset id: 11044
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an incorrect implementation of the ERC721 owner query function. The contract’s ownerOf routine returns the contract’s own address (address(this)) for every token identifier instead of the actual holder stored in the token‑owner mapping. This mistake originates from a logical error in the backward‑compatible ERC721 wrapper where the developer substituted the real owner lookup with a hard‑coded reference to the contract itself. Because ownerOf is the canonical source of truth for token ownership, any external call that relies on it – such as transferFrom, approve, or marketplace listings – will receive a false answer that the contract owns the token. An attacker or any caller can therefore be led to believe that the contract is the legitimate owner, which may allow unauthorized transfers, approvals, or other privileged actions that check ownership against the value returned by ownerOf. The impact is that legitimate token holders lose verifiable ownership; user interfaces may display a zero balance or show that the token is owned by the protocol, causing confusion and potentially preventing owners from transferring or selling their assets. The bug manifests whenever ownerOf is invoked, which is essentially every time a token’s ownership is queried, making it a pervasive condition. All participants who hold or interact with these NFTs – including end users, dApp developers, and the protocol itself – are affected because the fundamental accounting invariant of ERC721 (that each token has a unique external owner) is broken. The issue was uncovered during a manual security audit performed by MixBytes, where the auditor inspected the source code and identified the hard‑coded return value. It can be hard to notice in testing if the test suite does not explicitly verify ownerOf for a range of token IDs or if UI components do not surface the owner address. To remediate, the ownerOf function must be rewritten to read the owner from the internal mapping that tracks token ownership and return that address, thereby restoring the correct ownership semantics and preventing false ownership reports. In broader terms, this is a classic case of an ownership‑lookup bug that violates the ERC721 specification and undermines the protocol’s accounting guarantees, leading to user‑visible symptoms such as missing balances, zero‑value refunds, or inability to transfer tokens.

## Recommendation
Return real token owner instead of address(this)
