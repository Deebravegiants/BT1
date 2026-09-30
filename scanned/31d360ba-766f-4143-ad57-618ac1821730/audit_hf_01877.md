# [H] Lost nfts due to smart wallets having different addresses on different chains

## Summary
Severity: High
Contest weight: 0.0663
Dataset id: 10451
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability originates from a design assumption that the address invoking a token transfer function (send()) is also the intended recipient of the NFT. In many multi‑chain deployments the caller may be a smart contract wallet whose address is not identical on every blockchain – for example a wallet that is deployed separately on Ethereum, Polygon, or other EVM‑compatible chains. Because the contract unconditionally forwards the NFT to msg.sender, the token is minted or moved to the caller’s address on the current chain, which may be an address that the user does not control on that chain. This mismatch can cause the NFT to be locked in an inaccessible account, effectively disappearing from the user’s portfolio. The issue is triggered whenever a user interacts with the contract through a smart‑contract wallet that has distinct addresses across chains, such as a wallet created by a factory contract or a wallet that uses different address‑generation schemes per chain. From the user’s perspective the transaction appears successful – the UI shows a “transfer completed” message – but the NFT balance shown in the wallet becomes zero or the NFT never appears in the expected account. The problem is subtle because the contract does not emit an explicit error and the blockchain records a valid transfer to the caller’s address, making it difficult to detect without manually checking the address mapping on each chain. The impact is loss of ownership of the NFT, which may represent significant monetary value, and it undermines the protocol’s accounting guarantees that each user’s assets remain under their control. The flaw was identified during a manual audit that examined the token‑transfer logic and recognized that the code does not account for cross‑chain address variance. To remediate the issue the contract should not rely on msg.sender as the destination; instead it should allow the caller to explicitly specify a destination address, or resolve the correct address through a trusted registry that maps a user’s universal identifier to the appropriate chain‑specific address. By decoupling the transfer destination from the caller, the contract ensures that NFTs are sent to an address the user actually controls, preserving asset integrity across all supported chains.

## Recommendation
Let the user specify a destination address to send the nfts to.
