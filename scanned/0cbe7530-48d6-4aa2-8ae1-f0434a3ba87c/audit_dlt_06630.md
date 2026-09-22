# [H] Merging and Splitting of positions will break for certain tokens

## Summary
Severity: High
Chain: Smart contract
Component: SeeR-PM
Published: 2024-09-27
Source: https://github.com/hats-finance/SeeR-PM-0x899bc13919880db76edf4ccd72bdfa5dfa666fb7/issues/103
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x4d63d9ff89f7d82162d97b30dbcf04b6a83a30267e361d2a3b65c4509b9fe8dc
**Severity:** high

**Description:**
Description:

In the `Router` contract, the `mergePositions()` and `redeemPositions()` functions use `transfer` to transfer the `collateralToken` to the sender. Additionally, `transferFrom()` is used in the `splitPosition()` function. This will break for tokens that do not revert but return false on failure of transfer. The most well known ones of these being [EURS](https://etherscan.io/token/0xdb25f211ab05b1c97d595516f45794528a807ad8#code), an euro stablecoin with over 120M EUR in circulation.

Attack Scenario:

Tokens not compliant with the ERC20 specification could return false from the transfer function call to indicate the transfer fails, while the calling contract would not notice the failure if the return value is not checked. Checking the return value is a requirement, as written in the EIP-20 specification: "Callers MUST handle false from returns (bool success). Callers MUST NOT assume that false is never returned!". As a result, a user's position could be merged, but his token would never be transferred to him. This would result in him losing funds.

Attachments

Use [OpenZeppelin SafeERC20](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/utils/SafeERC20.sol)
