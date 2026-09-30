# [M] Early user can call `issue

## Summary
Severity: Medium
Contest weight: 0.6645
Dataset id: 18082
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Function `melt()` melt a quantity of RToken from the caller’s account, increasing the basket rate. basket rate should be between `1e9` and `1e27` and function `requireValidBUExchangeRate()` checks that if it’s not in interval the the code would revert. the call to `requireValidBUExchangeRate()` happens in the function `mint()`, `melt()` and `setBasketsNeeded()` which are used in `issue()` and `handoutExcessAssets()` and `compromiseBasketsNeeded()` which are used in multiple functionality of the systems. early malicious user can call `issue(1e18)` and `melt(1e18 - 1)` and then set the ratio between baskets needed and total supply to `1e27` and then any new action that increase the ratio would fail. because during the `issue()` code calls `melt()` so the issue() would fail for sure and other functionalities can increase the ratio because of the ratio too because of the rounding error which result in revert. so by exploiting this attacker can make RToken to be in broken state and most of the functionalities of the system would stop working.

## Proof of Concept
This is `melt()` code:
```solidity
function melt(uint256 amtRToken) external notPausedOrFrozen {
    _burn(_msgSender(), amtRToken);
    emit Melted(amtRToken);
    requireValidBUExchangeRate();
}
```
As you can see it allows anyone to burn their RToken balance. This is `requireValidBUExchangeRate()` code:
```solidity
function requireValidBUExchangeRate() private view {
    uint256 supply = totalSupply();
    if (supply == 0) return;

    // Note: These are D18s, even though they are uint256s. This is because
    // we cannot assume we stay inside our valid range here, as that is what
    // we are checking in the first place
    uint256 low = (FIX_ONE_256 * basketsNeeded) / supply; // D18{BU/rTok}
    uint256 high = (FIX_ONE_256 * basketsNeeded + (supply - 1)) / supply; // D18{BU/rTok}

    // 1e9 = FIX_ONE / 1e9; 1e27 = FIX_ONE * 1e9
    require(uint192(low) >= 1e9 && uint192(high) <= 1e27, "BU rate out of range");
}
```
As you can see it checks and makes sure that the BU to RToken exchange rate to be in [1e-9, 1e9]. so Attacker can perform this steps:

  1. add `1e18` RToken as first issuer by calling `issue()`
  2. call `melt()` and burn `1e18 - 1` of his RTokens.
  3. not `basketsNeeded` would be `1e18` and `totalSupply()` of RTokens would be `1` and the BU to RToken exchange rate would be its maximum value `1e27` and `requireValidBUExchangeRate()` won’t allow increasing the ratio.
  4. now calls to `melt()` would revert and because `issue()` calls to `furnace.melt()` which calls `RToken.melt()` so all calls to `issue()` would revert. other functionality which result in calling `mint()`, `melt()` and `setBasketsNeeded()` if they increase the ratio would fail too. as there is rounding error when converting RToken amount to basket amount so burning and minting new RTokens and increase the ratio too because of those rounding errors and those logics would revert. (`handoutExcessAssets()` would revert because it mint revenue RToken and update `basketsNeeded` and it calculates new basket amount based on RToken amounts and rounds down so it would increase the BU to RToken ratio which cause code to revert in `mint()`) (`redeem()` would increase the ratio simillar to `handoutExcessAssets()` because of rounding down)
  5. the attacker doesn’t need to be first issuer just he needs to be one of the early issuers and by performing the attack and also if the ratio gets to higher value of the maximum allowed the protocol won’t work properly as it documented the supported rage for variables to work properly.

So attacker can make protocol logics to be broken and then RToken won’t be useless and attacker can perform this attack to any newly deployed RToken.

## Recommendation
Don’t allow everyone to melt their tokens or don’t allow melting if totalSupply() become very small.

Understand that `issue()` plus `melt()` can brick an RTokens issuance, but redeem should still work. 

So, the RToken would no longer function as expected but no RToken holder funds would be lost. And in fact, RToken holders now have more funds.
 
Believe this is severity 2 but we should mitigate so that an annoying person / entity cannot DDOS every RToken on deployment w/ small amounts of capital. RToken holders can always continue to redeem though.

Agreed on downgrading due to no direct loss of significant funds and this mostly being a griefing type attack.

This PR prevents melting RToken until the RToken supply is at least 1e18: [reserve-protocol/protocol#619](https://github.com/reserve-protocol/protocol/pull/619)
