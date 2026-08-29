# [M] Manipulation of governance is possible by minti...

## Summary
Severity: Medium
Chain: Smart contract
Component: ZeroLend
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ZeroLend/28987%20-%20%5BSC%20-%20Medium%5D%20Manipulation%20of%20governance%20is%20possible%20by%20minti....md
Type: immunefi-boost

## Details
Target: https://github.com/zerolend/governance

## Description

## Brief/Intro

VestedZeroNFT::mint is `accessible to anyone`, so anyone can mint a VestedNFT in the moment. This seems to be against the expected behavior as noted as follow by the `IVestedZeroNFT` interface and seems to warrant `Critical` vulnerability for the vote manipulation exploit this could allow.

```
Mints a vesting nft for a user. This is a privileged function meant to only be called by a contract or a deployer
```

## Vulnerability Details

As indicated, it's possible to mint to self and with no duration (linearDuration = 0 and cliffDuration = 0), which mean already all claimable, and then the attacker can transfer the NFT to the `StakingBonus contract` in order to boost his voting power right away.

## Impact Details

Manipulation of governance is possible by minting to self a VestedNFT with no duration.

## References

https://github.com/zerolend/governance/blob/main/contracts/vesting/VestedZeroNFT.sol#L63-L100

## Proof of Concept

Add the following changes in `StakingBonus.test.ts` and run `npm test` command. The test proove the following:

1. Can mint to self with no duration
2. Boost in voting power confirmed

```diff
     beforeEach(async () => {
       expect(await vest.lastTokenId()).to.equal(0);

-      // deployer should be able to mint a nft for another user
-      await vest.mint(
+      // fund the ant account. This could be earned from a normal vesting NFT or bought on the secondary market, just transfering from deployer here to make this simpler
```

_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ZeroLend/28987%20-%20%5BSC%20-%20Medium%5D%20Manipulation%20of%20governance%20is%20possible%20by%20minti....md_
