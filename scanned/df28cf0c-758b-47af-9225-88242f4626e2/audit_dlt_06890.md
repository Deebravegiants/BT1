# [M] The owner can mint all of the NFTs.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-05-runes
Published: 2022-05-04
Source: https://github.com/code-423n4/2022-05-runes-findings/issues/104
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-05-runes/blob/main/contracts/ForgottenRunesWarriorsMinter.sol#L257


# Vulnerability details

## Impact
In ForgottenRunesWarriorsMinter.teamSummon() the owner can mint unrestricted amount of NFTs. This is more of a design issue than an actual bug in my opinion. 


## Proof of Concept

If the private keys were compromised during the launch the attacker could mint almost all of the NFTs. Normally I wouldn't say this is an issue but from your documentation, I understand that you are not planning to use a multi-sig wallet for the owner of the contracts. I definitely don't want to say that you are incompetent and you can't store your private keys safely but private keys are getting compromised very often in this space.  


## Tools Used
Manual Review

## Recommended Mitigation Steps

Limit how many NFTs can the owner mint. So even if the private keys were compromised the attacker couldn't destroy the entire set by minting thousands of the NFTs to himself making the entire set worth nothing.

I also think this will help with the trust of the protocol since the buyers will know exactly how many NFTs can the Dev Team mint for themselves.
