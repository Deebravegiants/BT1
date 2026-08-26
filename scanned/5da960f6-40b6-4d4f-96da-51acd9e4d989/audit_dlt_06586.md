# [H] Ineffective slippage protection allows for sandwich attacks

## Summary
Severity: High
Chain: Smart contract
Component: Fenix-
Published: 2024-07-10
Source: https://github.com/hats-finance/Fenix--0x9d7765a7ebd5b6322a30797a44a5428531970d3d/issues/17
Type: hats-finding

## Details
**Github username:** @0xEVom
**Twitter username:** 0xEV_om
**Submission hash (on-chain):** 0xfb6d84599a705570ed42038ea783841ff0f1fb4361604aec2036480cc78cb588
**Severity:** high

**Description:**
**Description**\
The `buybackTokenByV2()` function in the `SingelTokenBuybackUpgradeable` contract is designed to perform token buybacks using a DEX router. It calculates the expected output amount based on the current market conditions and applies a user-specified slippage tolerance. However, the current implementation of slippage protection is ineffective and leaves users vulnerable to sandwich attacks.

The function calculates the minimum output amount (`amountOutQuote`) within the same transaction as the swap execution. This approach has two major flaws:

1. The calculation is based on the current state of the liquidity pool, which can be manipulated by an attacker just before the transaction is executed.
2. The slippage is applied as a percentage of this potentially manipulated quote, rather than being an absolute minimum output amount provided by the user.

As a result, an attacker can front-run the transaction with a large swap to significantly impact the price, causing the user's transaction to receive far fewer tokens than expected, even with the applied slippage protection.

The relevant part of the `buybackTokenByV2()` function is:

```solidity
File: SingelTokenBuybackUpgradeable.sol
161:         amountOutQuote = amountOutQuote - (amountOutQuote * slippage_) / SLIPPAGE_PRECISION;
162:         if (amountOutQuote == 0) {
163:             revert RouteNotFound();
164:         }
165: 
166:         IRouterV2 router = IRouterV2(routerV2PathProviderCache.router());
167:         inputTokenCache.safeApprove(address(router), amountIn);
168: 
169:         uint256 balanceBefore = IERC20(targetToken).balanceOf(address(this));
170: 
171:         uint256[] memory amountsOut = router.swapExactTokensForTokens(amountIn, amountOutQuote, optimalRoute, address(this), deadline_);
```

**Attack Scenario**\
1. Alice initiates a buyback transaction with a 1% slippage tolerance.
2. The contract calculates `amountOutQuote` based on the current pool state, expecting to receive 1000 tokens.
3. An attacker front-runs Alice's transaction with a large swap, significantly impacting the price.
4. Alice's transaction is executed, but due to the price manipulation, the new `amountOutQuote` is now only 800 tokens.

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Fenix--0x9d7765a7ebd5b6322a30797a44a5428531970d3d/issues/17_
