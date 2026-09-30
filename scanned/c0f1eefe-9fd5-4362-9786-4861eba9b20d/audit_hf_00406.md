# [M] A `pauser` can brick the contracts

## Summary
Severity: Medium
Contest weight: 0.1522
Dataset id: 1805
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[Pausable.sol#L65-L68](https://github.com/code-423n4/2022-03-biconomy/blob/db8a1fdddd02e8cc209a4c73ffbb3de210e4a81a/contracts/security/Pausable.sol#L65-L68)  

        function renouncePauser() external virtual onlyPauser {
            emit PauserChanged(_pauser, address(0));
            _pauser = address(0);
        }

A malicious or compromised `pauser` can call `pause()` and `renouncePauser()` to brick the contract and all the funds can be frozen.

## Proof of Concept
Given:
  * Alice (EOA) is the `pauser` of the contract.
  * Alice calls `pause()` ;
  * Alice calls `renouncePauser()`;
As a result, most of the contract’s methods are now unavailable, and this cannot be reversed even by the `owner`.

## Recommendation
Consider removing `renouncePauser()`, or requiring the contract not in `paused` mode when `renouncePauser()`.

Yeah, `changePauser` needs to have an `onlyOwner` modifier instead of `onlyPauser`.
 
[HP-25: C4 Audit Fixes, Dynamic Fee Changes bcnmy/hyphen-contract#42](https://github.com/bcnmy/hyphen-contract/pull/42)

A valid concern, however, the proposed solution has drawbacks too. If you change from onlyPauser to onlyOwner here, a compromise of the owner account will have devastating consequences while with the current implementation the pauser can still pause the contracts independently of an owner. So this is a double-edged sword, it is up to you to decide which way is more acceptable.
