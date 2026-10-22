# [M] Tokens with non-string metadata revert

## Summary
Severity: Medium
Contest weight: 0.0335
Dataset id: 13539
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability originates from an incompatibility between the ERC20 specification and the actual implementation of some legacy tokens. The ERC20 standard defines the name() and symbol() functions to return a dynamically‑sized string, but a handful of tokens – for example Maker (MKR) – implement these functions to return a fixed‑size bytes32 value. When the Phuture V2 contract queries token metadata using a staticcall that expects a string, the call fails because the returned data does not match the expected ABI encoding. The staticcall therefore returns false and the contract reverts with a custom error. This mismatch is a classic ABI‑type mismatch bug that manifests as a denial‑of‑service condition: any operation that relies on retrieving a token’s name or symbol – such as registering a new currency, displaying token information in a UI, or performing cross‑chain messaging – will abort when encountering a non‑string implementation. From a user’s perspective the symptoms are missing or empty token names and symbols, UI elements that show blank fields, or transactions that revert without a clear error message. The issue was discovered during a manual audit when the auditor attempted to read metadata from several tokens and observed that calls to name() and symbol() reverted for tokens that use bytes32. Because most tokens follow the spec, the problem can be easy to overlook until a deviating token is introduced. The impact is medium: it does not directly lead to loss of funds, but it can halt protocol functionality, prevent users from seeing correct token information, and potentially be abused by an attacker who deploys a malicious token that deliberately returns bytes32 to trigger repeated reverts. The appropriate mitigation is to add a helper that performs a staticcall, checks the length of the returned data, and if it is exactly 32 bytes treats it as a bytes32 value, converts it to a string by trimming trailing zeros, and otherwise decodes it as a normal string. This approach restores compatibility with both compliant and legacy tokens, eliminating the revert and allowing the protocol to continue operating as intended.

## Recommendation
The following fix provides compatibility for both string and bytes32:
