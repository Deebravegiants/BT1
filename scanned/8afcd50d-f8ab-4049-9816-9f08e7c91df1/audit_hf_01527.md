# [M] The owner can mint all of the NFTs.

## Summary
Severity: Medium
Contest weight: 0.1883
Dataset id: 8124
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[ForgottenRunesWarriorsMinter.sol#L257](https://github.com/code-423n4/2022-05-runes/blob/main/contracts/ForgottenRunesWarriorsMinter.sol#L257)  

In ForgottenRunesWarriorsMinter.teamSummon() the owner can mint unrestricted amount of NFTs. This is more of a design issue than an actual bug in my opinion.

## Proof of Concept
If the private keys were compromised during the launch the attacker could mint almost all of the NFTs. Normally I wouldn’t say this is an issue but from your documentation, I understand that you are not planning to use a multi-sig wallet for the owner of the contracts. I definitely don’t want to say that you are incompetent and you can’t store your private keys safely but private keys are getting compromised very often in this space.

## Recommendation
Limit how many NFTs can the owner mint. So even if the private keys were compromised the attacker couldn’t destroy the entire set by minting thousands of the NFTs to himself making the entire set worth nothing.

I also think this will help with the trust of the protocol since the buyers will know exactly how many NFTs can the Dev Team mint for themselves.

This is true, but by design. It’s a risk for minters, but it would be obvious, so we’re economically disincentivized to do this. Acknowledged, but not changing it.

Sponsor acknowledged centralization risk in README.

Centralization risk in general is one thing, the ability for unlimited mint, which is easily fixable, is another.
 
A kind of a boundary state here in my opinion, having ‘acknowledged’ and ‘invalid’ flags in the same time poses some contradiction.

Judging this as Med Risk since there are specified amounts of teamSummon in the doc
>
> Forgotten Council DAO Creators Fund (teamSummon): ~333  
>  Team & Partners (teamSummon): ~325  
>  Community Honoraries and Contests (teamSummon): ~50  
> 
> 
> which is not enforced in the `teamSummon` function.
