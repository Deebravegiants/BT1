# [M] setConvictionless can be front-run to prevent conviction reset

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-05-fairside
Published: 2021-05-26
Source: https://github.com/code-423n4/2021-05-fairside-findings/issues/23
Type: code-finding

## Details
# Handle

0xRajeev


# Vulnerability details

## Impact

The denylist convictionless is meant to deny conviction scores for certain users and is set by the privileged roles timelock/FSD-owner in setConvictionless(). The documentation says: “adjust which addresses are meant to not accrue a conviction score. The latter part is crucial and should be applied to "static" FSD token holders such as the burn address to ensure that the conviction score tribute rewards and governance quorums are correctly calculated.”

It is not clear if the addresses meant to not accrue a conviction score are a few well-known static ones or if this can be used as a denylist in general for misbehaving participants.

If this is indeed used as a general denylist for a misbehaving user say Alice, upon seeing a setConvictionless(Alice, True) call in the mempool, Alice can front-run that transaction which tries to add her to the denylist by simply transferring the tokens to another address or tokenizing it into a NFT, transferring that to another address and then re-acquiring the conviction score on that address.

The impact will be that setConvictionless will fail to achieve its denylist action.


## Proof of Concept

https://github.com/code-423n4/2021-05-FairSide/blob/3e9f6d40f70feb67743bdc70d7db9f5e3a1c3c96/contracts/token/FSD.sol#L251-L261


## Tools Used

Manual Analysis

## Recommended Mitigation Steps

Use commit/reveal scheme on the user address being made convictionless to prevent this scenario.
