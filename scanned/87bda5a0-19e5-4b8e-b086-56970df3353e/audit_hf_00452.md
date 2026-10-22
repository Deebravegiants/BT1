# [H] Cross-Chain Signature Replay

## Summary
Severity: High
Contest weight: 0.6053
Dataset id: 1878
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol is deployed across multiple EVM-compatible chains (Bitlayer, Botanix, Core, and Ethereum) with separate instances of Multisig.sol and Bridge.sol. The Multisig.sol contract uses the call() function to execute transactions authenticated by admin signatures. However, the payload for these signatures is not chain-specific, making the signature valid across different chains.
This vulnerability allows an attacker to replay a valid signature from one chain to execute unauthorized transactions on another chain.
The payload hash used for signature creation and verification does not include chain-specific data, making signatures chain-agnostic:
```solidity
bytes32 payload = keccak256(abi.encode(nonce, target, value, data));
bytes32 hash = keccak256(abi.encodePacked("\x19Ethereum Signed Message:\n32", payload));
```
This design flaw allows a signature created on one chain to be reused for transaction execution on another chain.
Payload Signature Verification
Internal pre-conditions
External pre-conditions
Attack Path
1. Valid signatures are used by Bridge to call call() function on chain A.
2. Attacker sees the transaction data, signatures.
3. Use same signature and data on chain B.
1. Unauthorized transactions can be executed across chains using the same signatures.
2. Loss of funds if the target address on another chain contains different logic.
3. Unauthorized minting or unlocking of assets on other chains.

## Recommendation
To prevent signature replay across chains, follow the EIP-712 standard for signature creation and verification, which includes chain-specific data (chainId / targetNetwork).
