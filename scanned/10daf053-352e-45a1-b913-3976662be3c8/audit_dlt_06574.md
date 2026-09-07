# [M] `PALMERA_TX_TYPEHASH` incorrectly calculated

## Summary
Severity: Medium
Chain: Smart contract
Component: Palmera
Published: 2024-06-24
Source: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/1
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x0fd83a8c3c07269645329ee58706a552b4596aa4583bd6ded0b7d29bfa1b15c1
**Severity:** medium

**Description:**
## Description

The constant `PALMERA_TX_TYPEHASH` in the contract **Constants** is incorrectly calculated

## Attack Scenario

This breaks [EIP-721](https://eips.ethereum.org/EIPS/eip-712)

## Attachments

### PoC

https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/blob/dfd821e2fd7825c66c079c19be9460238f6e045a/src/libraries/Constants.sol#L16-L20

```solidity
    /// @dev keccak256(
    ///     "PalmeraTx(address org,address superSafe,address targetSafe,address to,uint256 value,bytes data,uint8 operation,uint256 _nonce)"
    /// );
    bytes32 internal constant PALMERA_TX_TYPEHASH =
        0x5576bff5f05f6e5452f02e4fe418b1519cb08f54fae3564c3a4d2a4706584d4e;
```

Should be:

```solidity
    /// @dev keccak256(
    ///     "PalmeraTx(address org,address superSafe,address targetSafe,address to,uint256 value,bytes data,uint8 operation,uint256 _nonce)"
    /// );
    bytes32 internal constant PALMERA_TX_TYPEHASH =
        0x33d86b91ace2c23c833e6a968f94ce2cdabd89ed7375f3d2135aa0f5a9c131b5;
```
