# [M] M-13 Use general safeTransferFrom

## Summary
Severity: Medium
Contest weight: 0.0353
Dataset id: 7925
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of using a token transfer method that does not verify whether the transfer succeeded, specifically calling a low‑level transfer routine instead of the ERC‑721 safeTransferFrom function. The root cause is the omission of a success check after the call, which means the contract proceeds as if the token moved even when the underlying call returned false or reverted silently. An attacker can exploit this by sending a token to a malicious or non‑compliant contract that does not implement the ERC721Receiver interface; the transfer will fail, but because the caller does not inspect the return value, the contract records the token as transferred while the asset remains locked in the recipient address. The impact is that users may lose access to their NFTs, see their balances drop to zero, or experience refunds that never arrive, effectively causing funds to disappear from the expected holder. This condition occurs whenever the contract executes the transfer at the indicated lines, typically during minting, marketplace sales, or any internal token movement that relies on the unchecked call. All participants who interact with the NFT – owners, buyers, sellers, and the protocol itself – are affected because the accounting assumptions of the system (that a successful transfer updates ownership) are violated. The issue was discovered during a manual audit where the code paths were examined and the lack of a require‑style check was noted. It can be hard to notice because the transaction may not revert and no explicit error is emitted; the UI may simply show a successful operation while the token never appears in the recipient’s wallet. The proper remediation is to replace the unchecked transfer with the standard safeTransferFrom function, which includes an internal check that the recipient implements the required interface and reverts on failure, thereby guaranteeing that ownership changes only when the transfer truly succeeds. This class of bug falls under unchecked external calls or unsafe token transfers, a common source of asset loss in smart contracts. From the user’s perspective the symptom is a missing NFT after a purchase – the user expects to receive the token but the balance remains unchanged or shows zero, leading to confusion and potential loss of funds. The failure mode breaks the accounting logic of the protocol, allowing tokens to become irretrievable without additional recovery mechanisms.

## Recommendation
It is recommended to always use the safeTransferFrom() function when sending tokens.
2.4 Low
