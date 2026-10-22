# [M] M-02 Unmitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-02-renft-mitigation
Published: 2024-03-02
Source: https://github.com/code-423n4/2024-02-renft-mitigation-findings/issues/10
Type: code-finding

## Details
# Lines of code

https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/policies/Fallback.sol#L116


# Vulnerability details

## C4 Issue

M-02: [A malicious borrower can hijack any NFT with `permit()` function he rents](https://github.com/code-423n4/2024-01-renft-findings/issues/587)

## Comments

Users were able to call `permit()` on NFTs, which would approve the token for later being able to transfer them out of the wallet despite being rented.

## Mitigation

[PR-11](https://github.com/re-nft/smart-contracts/pull/11): Prevent permit() tokens from validating permit signature in rental safe

- A [Fallback policy has been created](https://github.com/re-nft/smart-contracts/pull/11/files#diff-ba70ad171d96d1eae0eb15fa0ef7fb131bb40db5d469b1f530419486d27a0271) to solve the issue
- Calls to `permit()` verify signatures on wallets via `isValidSignature()`, like in [the example provided in the report](https://github.com/Uniswap/v3-periphery/blob/main/contracts/base/ERC721Permit.sol#L77)
  - `isValidSignature()` is implemented according to the interface described in [EIP-1271](https://eips.ethereum.org/EIPS/eip-1271), and returns the [`0x1626ba7e`](https://github.com/re-nft/smart-contracts/pull/11/files#diff-ba70ad171d96d1eae0eb15fa0ef7fb131bb40db5d469b1f530419486d27a0271R31) value on success as described by the EIP
- The callback validates that the sender (the NFT verifying the permit) is not a whitelisted token, [otherwise it will revert](https://github.com/re-nft/smart-contracts/pull/11/files#diff-ba70ad171d96d1eae0eb15fa0ef7fb131bb40db5d469b1f530419486d27a0271R115-R118)


With these additions, if a user calls `permit()` on a whitelisted token, `isValidSignature()` will revert. But if executed on any other contract/token, it will verify the signature as expected, approving the tokens.

## Mitigation Problems

### Impact

Unwhitelisting tokens will allow users to call `permit()` on the rented tokens, validate the signature, and approve the tokens for transferring them

### Vulnerability Details

Whitelisting assets [is an on/off switch](https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/modules/Storage.sol#L392-L397).

`isValidSignature()` checks that the token [is **currently** on the whitelisted assets list](https://github.com/re-nft/smart-contracts/pull/11/files#diff-ba70ad171d96d1eae0eb15fa0ef7fb131bb40db5d469b1f530419486d27a0271R116).

So, the moment a whitelisted asset is removed (so that no new rentals are created with it), the `permit()` function will be executable, as the `isValidSignature()` will not revert anymore.

### Recommended Mitigation Steps

One option is to implement a bitmap for `whitelistedAssets`, as was done with other whitelists.

## Conclusions

Insufficient Mitigation


## Assessed type

Invalid Validation
