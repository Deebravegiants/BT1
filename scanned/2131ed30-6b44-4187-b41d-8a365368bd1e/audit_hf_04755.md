# [M] Medium5-CrossChainWETHSwapFeesChargedUnnec

## Summary
Severity: Medium
Contest weight: 0.5979
Dataset id: 22597
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When doing a cross-chain transfer with any valid fromToken, using sgETH as bridgeToken and WETH as toToken via the WooRouterV2 swap on destination chain. The user is charged an unnecessary fee. When receiving a cross-chain swap trhough sgReceive() at WooCrossChainRouterV4, if the bridgeToken is sgETH then the _handleNativeReceived() will be called. This function if toToken != ETH_PLACEHOLDER_ADDR will perform a swap to change the eth used as bridgeToken for the toToken using, for example, the very same WooRouterV2. And for exchanging ETH it needs to be wrapped up as WETH which it does by calling IWETH(weth).deposit{value: bridgedAmount}();. The problem comes when the toToken desired is WETH, then a WETH to WETH swap will be carried out by the WooRouterV2 which will result in a fee being charged to the user due to a swap which makes no sense but would execute. So the user is losing unnecessary unexpected money. You can see that WooRouterV2 allows for swaps where from and to tokens are the same token exeuting the following code: To run the code copy paste it inside the ./test/typesript/WooRouterV2.test.sol file, then inside the describe("Swap Functions", () => {}), and then after the beforeEach("Deploy WooRouterV2", async () => {}), and then run: npx hardhat test test/typescript/WooRouterV2.test.ts
```solidity
it.only("swap btc -> btc", async () => {
await btcToken.mint(user.address, ONE.mul(5));
console.log("POOL BTC BALANCE", await utils.formatEther(await btcToken.balanceOf(wooPP.address)));
console.log("Swap: btc -> btc");
const fromAmount = ONE.mul(2);
const minToAmount = ONE.mul(1);
await btcToken.connect(user).approve(wooRouter.address, fromAmount);
await wooRouter
.connect(user)
.swap(btcToken.address, btcToken.address, fromAmount, minToAmount, user.address, ZERO_ADDR);
console.log("POOL BTC BALANCE", await utils.formatEther(await btcToken.balanceOf(wooPP.address)));
console.log("That means from the 2 BTC user sent only 0.002 were left as fee.");
console.log("What matters for our issue is that the tx succeeded and a fee was taken.");
});
```
require(toToken != WETH && brdigeToken != sgETH) anywhere. swaps go through this problem would apply. But if the tx reverts this problem wouldn't apply as the swapping fee of 1inch wouldn't be applied and the transfer of bridgeAmount would take place as expected. Due to personal lack of time I let this question open. Anyway the recommendation proposed would fix the problem too in case 1inch also allows execution of the unnecessary swap. Users lose unnecessary money when doing a cross-chain transfer with sgETH as bridgeToken and WETH as toToken via the WooRouterV2 swap on detination chain.

## Recommendation
At _handleNativeReceived(). In the case of bridging with sgETH, after the if(toToken == ETH_PLACEHOLDER_ADDR){}, add an extra if that checks if toToken != WETH, and if they are indeed different proceed with the swap.
```solidity
if (toToken == ETH_PLACEHOLDER_ADDR) {
// code for when no swap required...
}
IWETH(weth).deposit{value: bridgedAmount}();
if (toToken != WETH) {
// Swap required!
// Swap logic...
}else{
// send the WETH
}
```
