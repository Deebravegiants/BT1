# [H] Malicious user can transfer all unclaimed rewar...

## Summary
Severity: High
Chain: Smart contract
Component: ZeroLend
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ZeroLend/28955%20-%20%5BSC%20-%20High%5D%20Malicious%20user%20can%20transfer%20all%20unclaimed%20rewar....md
Type: immunefi-boost

## Details
Target: https://github.com/zerolend/governance

## Description

## Brief/Intro

A malicious user can distribute reward tokens to a specific pool gauge through distributeEx function at PoolVoter without resetting claimable mapping.

## Vulnerability Details

There are two distribute methods in PoolVoter. a distribute function, which is intended to transfer any claimable reward of a gauge and notifyRewardAmount in that gauge then reset claimable mapping , also there is a distributeEx function which is intended to distribute additional rewards proportionally to all gauges, it takes a rewards token address (a token that would be distributed ) and several pool addresses to distribute rewards, the distributed amount has been calculated based on pool weight proportion to the total weight. however, it doesn't check the token address provided as the parameter is not the main reward token, so the main reward token can be transferred through this function without resetting claimable mapping, which enables transferring more yield to a specific gauge, leading to a situation which contract doesn't have enough balance to distribute reward of other gauges. most rewards can transferred to a gauge to benefit the attacker.

## Impact Details

Malicious users can transfer more rewards to a gauge ( almost all rewards ), in favor of themselves, which is considered direct theft of unclaimed yields.

## References

https://github.com/zerolend/governance/blob/a30d8bb825306dfae1ec5a5a47658df57fd1189b/contracts/voter/PoolVoter.sol#L214-L234 https://github.com/zerolend/governance/blob/a30d8bb825306dfae1ec5a5a47658df57fd1189b/contracts/voter/PoolVoter.sol#L181-L190

## Proof of Concept

```
describe("transfer rewards test", () => {
  it("Malicious user can transfer all rewards to a speciefic gauge", async function () {
  
  // NOTE: this test works with https://github.com/zerolend/governance/commit/4c18c037bd3360ec7316733478b67632fb5218c9 commit 
  // tests didn't work at latest commit, however there is no change at pool voter other than changing some variable names between two commits 
  // so there is no differece 
  // some parts has been added to deployement as follow
  // a new lending pool has been deployed during deployment and its gauge has been registered at pool voter during deployment 
  // some zero tokens has been transferred to ant.address, so ant.address have enough zero token balance 
  // there is an issue at line 136 of PoolVoter by missing a ! sign, which prevents adding pools to _pool array and preventing distribute rewards 
  // since this issue relates to distributing rewards I needed to fix that so distribute function works by fixing if statement 
  // however I submitted that issue seperately and its different from this issue 

  // voting to both gauges equally 
  let vote1 = 1e8/2;
```

_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ZeroLend/28955%20-%20%5BSC%20-%20High%5D%20Malicious%20user%20can%20transfer%20all%20unclaimed%20rewar....md_
