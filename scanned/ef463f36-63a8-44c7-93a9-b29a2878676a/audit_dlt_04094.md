# [M] Medium5-CrossChainWETHSwapFeesChargedUnnecesarily

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-03-woofi-swap
Published: 2024-03-20
Source: https://github.com/sherlock-audit/2024-03-woofi-swap-judging/issues/95
Type: sherlock-finding

## Details
charles__cheerful

medium

# Medium5-CrossChainWETHSwapFeesChargedUnnecesarily

### by [CarlosAlegreUr](https://github.com/CarlosAlegreUr)

## Summary

When doing a cross-chain transfer with any valid `fromToken`, using `sgETH` as `bridgeToken` and **WETH** as `toToken` via the
`WooRouterV2` swap on destination chain. The user is charged an unnecessary fee. 

## Vulnerability Detail

When receiving a cross-chain swap trhough `sgReceive()` at `WooCrossChainRouterV4`, if the `bridgeToken` is **sgETH** then the `_handleNativeReceived()` will be called. This function if `toToken != ETH_PLACEHOLDER_ADDR` will perform a swap to change the eth used as `bridgeToken` for the `toToken` using, for example, the very same `WooRouterV2`. And for exchanging ETH it needs to be wrapped up as **WETH** which it does by calling `IWETH(weth).deposit{value: bridgedAmount}();`.

The problem comes when the `toToken` desired is **WETH**, then a ***WETH to WETH*** swap will be carried out by the `WooRouterV2` which will result in a fee being charged to the user due to a swap which makes no sense but would execute. So the user is losing unnecessary unexpected money.

You can see that `WooRouterV2` allows for swaps where `from` and `to` tokens are the same token exeuting the following code:

<details>
<summary>See swap the same `from` and `to` tokens via WooRouterV2 👁️</summary>

To run the code copy paste it inside the `./test/typesript/WooRouterV2.test.sol` file, then inside the `describe("Swap Functions", () => {})`, and then after the `beforeEach("Deploy WooRouterV2", async () => {})`, and then run:

```bash
npx hardhat test test/typescript/WooRouterV2.test.ts
```

```typescript
    it.only("swap btc -> btc", async () => {
      await btcToken.mint(user.address, ONE.mul(5));
      console.log("POOL BTC BALANCE", await utils.formatEther(await btcToken.balanceOf(wooPP.address)));
      console.log("Swap: btc -> btc");
      const fromAmount = ONE.mul(2);
      const minToAmount = ONE.mul(1);
      await btcToken.connect(user).approve(wooRouter.address, fromAmount);
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2024-03-woofi-swap-judging/issues/95_
