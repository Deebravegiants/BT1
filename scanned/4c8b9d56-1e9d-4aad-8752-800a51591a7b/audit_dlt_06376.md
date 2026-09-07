# [H] Curve reentrancy check for tokens being borrowed is missing

## Summary
Severity: High
Chain: Smart contract
Component: Wise-Lending
Published: 2024-02-18
Source: https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/issues/48
Type: hats-finding

## Details
**Github username:** @bahurum
**Twitter username:** bahurum
**Submission hash (on-chain):** 0x445cf137ddf578bc3c58b45f02850886f981c27fc76282da35a904c6b95d4c82
**Severity:** high

**Description:**
**Description**\
The function [`MainHelper._curveSecurityChecks()`](https://github.com/wise-foundation/lending-audit/blob/1637d6e455e81712b9b23c7f3ae80149d9631a35/contracts/MainHelper.sol#L455) will check for curve lp tokens price manipulation via read-only-reentrancy for all `_lendTokens` and `_borrowTokens` used by the `nftId`.

The issue is that in [`WiseCore._coreBorrowTokens()`](https://github.com/wise-foundation/lending-audit/blob/1637d6e455e81712b9b23c7f3ae80149d9631a35/contracts/WiseCore.sol#L329) the function `_prepareAssociatedTokens()` is called *before* `_addPositionTokenData()`, meaning that `_poolToken` isn't included in the `borrowTokens` array and the curve reentrancy check is not performed on it.

With read-only-reentrancy, the curve pool's `virtual_price` can be manipulated downwards, so the health check will allow to borrow more of the lp token than it should be allowed, at the profit of an attacker. 

**Attack Scenario**\
Consider this simplified scenario:
1. There are 1000 ETH worth of stETH/ETH lp token available for borrow.
2. Attacker takes flashloan of 500 ETH from some other protocol
3. Attacker deposits 500 ETH
4. Attacker manipulates curve lp virtual price to half its value
   and during the reentrant call:
   1. Attacker borrows 1000 ETH worth of stETH/ETH lp token
   2. No reentrancy check is performed because of the issue
   3. Because of the manipulation, during health check the value borrowed seen by the protocol is 500 ETH instead of 1000 ETH. Health check passes.
5. Attacker repays flash loans of 500 ETH and profits 500 ETH.
6. 500 ETH of bad debt is left in the protocol.

**Impact**\
Borrowable curve lp tokens with manipulatable virtual price can be drained from the protocol at a profit, leaving bad debt in the protocol.

**Recommendation**\
In `_coreBorrowTokens()`, add `_poolToken` to the `borrowTokens` array before passing it into `_curveSecurityChecks()`.

**Attachments**

1. **Proof of Concept (PoC) File**\
The issue is quite simple. I can provide a PoC later if requested.
