# [M] no use of safeMint

## Summary
Severity: Medium
Contest weight: 0.1673
Dataset id: 1479
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In `Vault.sol` the `deposit()` function eventually calls claimers.mint() and depositers.mint(). Calling mint this way does not ensure that the receiver of the NFT is able to accept them. `_safeMint()` should be used with reentrancy guards as a guard to protect the user as it checks to see if a user can properly accept an NFT and reverts otherwise.

## Proof of Concept
* <https://github.com/code-423n4/2022-01-sandclock/blob/main/sandclock/contracts/Vault.sol#L470>
  * <https://github.com/code-423n4/2022-01-sandclock/blob/main/sandclock/contracts/Vault.sol#L256>
  * <https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC721/ERC721.sol#L248>

## Recommendation
Use `_safeMint()` instead of `mint()`

**[ryuheimat (Sandclock) disagreed with severity](https://github.com/code-423n4/2022-01-sandclock-findings/issues/29#issuecomment-1007534909):**

I think _safeMint check if the recipient contract is able to accept NFT, it does not involves any issues. However we will use _safeMint.

@ryuheimat this is a non-issue. The mint functions called in the Vault’s deposit function are implemented by us, they just happen to be called mint.

The Depositors contract does use `_safeMint`, but the Claimers contract does not.
 
See: <https://github.com/code-423n4/2022-01-sandclock/blob/main/sandclock/contracts/vault/Claimers.sol#L63> <https://github.com/code-423n4/2022-01-sandclock/blob/main/sandclock/contracts/vault/Depositors.sol#L53>
 
The `deposit` function on Vault also appears to lack reentrancy guards. The issue is valid and should be addressed, despite the fact that the warden clearly did not look at the Depositors contract to see that it already used `_safeMint`.
