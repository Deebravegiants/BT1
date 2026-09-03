# [M] Assets in a Safe can be lost

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-01-renft
Published: 2024-01-18
Source: https://github.com/code-423n4/2024-01-renft-findings/issues/323
Type: code-finding

## Details
# Lines of code

https://github.com/re-nft/smart-contracts/blob/3ddd32455a849c3c6dc3c3aad7a33a6c9b44c291/src/policies/Guard.sol#L195-L293


# Vulnerability details

## Impact
The `Guard.sol` contract is enabled on Safe's and uses the [`_checkTransaction`](https://github.com/re-nft/smart-contracts/blob/3ddd32455a849c3c6dc3c3aad7a33a6c9b44c291/src/policies/Guard.sol#L195-L293) function to ensure that transactions that the Safe executes do not transfer the asset out of the Safe.

The `checkTransaction` function achieves this by isolating the function selector and checking that it is not a disallowed function selector. For instance: `safeTransferFrom`, `transferFrom`, `approve`, `enableModule`, etc.

The list does not, however, check for calls to `burn` the token, neither does it check if it is a `permit`. The sponsor has noted the following: 

> The
[Guard](https://github.com/re-nft/smart-contracts/blob/3ddd32455a849c3c6dc3c3aad7a33a6c9b44c291/src/policies/Guard.sol) contract can only protect against the transfer of tokens that faithfully
implement the ERC721/ERC1155 spec

But this does not acknowledge the fact that an ERC721/ERC1155 implementation can still be an honest implementation and have extra functionality. In particular, the `burn` function is a common addition to many ERC721 contracts, usually granted through inheriting `ERC721Burnable`.

For example, the following projects all have a `burn` function, and Safe's protected by `Guard.sol` that hold these NFTs will be vulnerable to loss of assets via a malicious renter:
- [Pudgy Penguins](https://etherscan.io/address/0xbd3531da5cf5857e7cfaa92426877b022e612cf8#writeContract)  
- [Lil Pudgies](https://etherscan.io/address/0x524cab2ec69124574082676e6f654a18df49a048#writeContract)
- [Oh Ottie](https://etherscan.io/address/0x7ff5601b0a434b52345c57a01a28d63f3e892ac0#code#F3#L45)

These are three that are in the top 10 projects on Opensea at the time of writing. 

## Proof of Concept
We can see in the `Guard.sol` file that certain function selectors are imported to be tested against:
```
import {
    shared_set_approval_for_all_selector,
    e721_approve_selector,
    e721_safe_transfer_from_1_selector,
    e721_safe_transfer_from_2_selector,
    e721_transfer_from_selector,
    e721_approve_token_id_offset,
    e721_safe_transfer_from_1_token_id_offset,
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-01-renft-findings/issues/323_
