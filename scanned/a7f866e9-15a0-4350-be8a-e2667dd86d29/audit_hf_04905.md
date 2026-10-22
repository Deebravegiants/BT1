# [M] Fee-on-transfer token is not integrated correctly

## Summary
Severity: Medium
Contest weight: 0.4616
Dataset id: 22821
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Fee-on-transfer token is not integrated correctly Context One: from contest readme: We will be using ERC20 tokens. The contract should handle the case where tokens have, for examples, fee for transfers. Context two: https://github.com/d-xo/weird-erc20?tab=readme-ov-file#fee-on-transfer Some tokens take a transfer fee (e.g. STA, PAXG), some do not currently charge a fee but may do so in the future (e.g. USDT, USDC). The STA transfer fee was used to drain $500k from several balancer pools (more details). But the Fee-on-transfer token is not integrated correctly in several ways: 1. code the only calls swapExactTokenForTokens, but if the token charge, they need to calls this method
```solidity
function swapExactTokensForTokensSupportingFeeOnTransferTokens(
    uint amountIn,
    uint amountOutMin,
    address[] calldata path,
    address to,
    uint deadline
) external virtual override ensure(deadline) {
    TransferHelper.safeTransferFrom(
        path[0], msg.sender, UniswapV2Library.pairFor(factory, path[0], path[1]), amountIn
    );
    uint balanceBefore = IERC20(path[path.length - 1]).balanceOf(to);
    _swapSupportingFeeOnTransferTokens(path, to);
    require(
        IERC20(path[path.length - 1]).balanceOf(to).sub(balanceBefore) >= amountOutMin,
        'UniswapV2Router: INSUFFICIENT_OUTPUT_AMOUNT'
    );
}
```
2. in Messi contract: } else { address bridgeTokenAddress = bridgeOp.inputToken; require(bridgeTokenAddress != address(0), "Messi: bridge token must not be 0x0"); require(bridgeOp.amountIn > 0, "Messi: bridge amount must be greater than 0"); IERC20 tokenToBridge = IERC20(bridgeTokenAddress); require( tokenToBridge.balanceOf(receivingUser) >= bridgeOp.amountIn, "Messi: balance not enough to bridge tokens as only op" ); require( tokenToBridge.allowance(receivingUser, address(this)) >= bridgeOp.amountIn, "Messi: allowance not enough to bridge tokens as only op" ); // We bring the tokens and approve the master proxy to operate them tokenToBridge.safeTransferFrom(receivingUser, address(this), bridgeOp.amountIn); } tokenToBridge.safeTransferFrom(receivingUser, address(this), bridgeOp.amountIn); the contract assumes that the contract always receives the amount bridgeOp.amountIn then use this bridgeOp.amountIn to start bridge operation. but if underlying token charges transfer fee, while the bridgeOp.amountIn is 10000, suppose 1% of fee is charged, the contract only receives 9900 token, then bridge 10000 token will revert. Lack of integration for fee-on-transfer token dit-v1/contracts/Paymaster/Messi.sol#L445 address bridgeTokenAddress = bridgeOp.inputToken; require(bridgeTokenAddress != address(0), "Messi: bridge token must not be 0x0"); require(bridgeOp.amountIn > 0, "Messi: bridge amount must be greater than 0"); IERC20 tokenToBridge = IERC20(bridgeTokenAddress); require( tokenToBridge.balanceOf(receivingUser) >= bridgeOp.amountIn, "Messi: balance not enough to bridge tokens as only op" ); require( tokenToBridge.allowance(receivingUser, address(this)) >= bridgeOp.amountIn, "Messi: allowance not enough to bridge tokens as only op" ); // We bring the tokens and approve the master proxy to operate them tokenToBridge.safeTransferFrom(receivingUser, address(this), bridgeOp.amountIn);

## Recommendation
1. support method swapExactTokensForTokensSupportingFeeOnTransferTokens 2. whenever there are safeTransferFrom, use balance before / after to validate the actual amount of received.
