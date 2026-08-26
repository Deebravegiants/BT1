# [H] In ZetaTokenConsumerTrident. strategy.sol, swapping zeta for other tokens will always revert due to incorrect exactInputSingle router method  being used

## Summary
Severity: High
Chain: Smart contract
Component: 2023-11-zetachain
Published: 2023-12-17
Source: https://github.com/code-423n4/2023-11-zetachain-findings/issues/387
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L159


# Vulnerability details

## Impact
Swapping zeta for other tokens through `getZetaFromToken()` will always revert in ZetaTokenConsumerTrident.strategy.sol, due to calling the incorrect `exactInputSingle` router method.

## Proof of Concept
In ZetaTokenConsumerTrident.strategy.sol, when swapping other tokens for zetaToken, `getZetaFromToken()` will be called and the function will first transfer inputToken from caller and approve `tridentRouter` to spend `inputTokenAmount`. Then it will call `tridentRouter.exactInputSingle(params)` for `tridentRouter` to execute token swap. 

However, `exactInputSingle()` is the incorrect function for the use case and will always revert. In current TridentRouter.sol implementation, bento balance will be called to transfer from ZetaTokenConsumerTrident.strategy.sol first, but ZetaTokenConsumerTrident.strategy.sol doesn't have means to deposit into bento, neither will it approve `TridentRouter` to manage it's bento tokens. 
```solidity
//contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
    function getZetaFromToken(
        address destinationAddress,
        uint256 minAmountOut,
        address inputToken,
        uint256 inputTokenAmount
    ) external override returns (uint256) {
...
        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
        IERC20(inputToken).safeApprove(address(tridentRouter), inputTokenAmount);
        (address token0, address token1) = getPair(zetaToken, WETH9Address);
        address[] memory pairPools = poolFactory.getPools(token0, token1, 0, 1);
        IPoolRouter.ExactInputSingleParams memory params = IPoolRouter.ExactInputSingleParams({
            tokenIn: zetaToken,
            amountIn: zetaTokenAmount,
            amountOutMinimum: minAmountOut,
            pool: pairPools[0],
            to: destinationAddress,
            unwrap: true
        });
        //@audit tridentRouter.exactInputSingle will not transfer inputToken, but only tries to transfer bento shares which this contract has no means to deposit nor approve. This will cause transaction revert.
|>      uint256 amountOut = tridentRouter.exactInputSingle(params);
...
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-11-zetachain-findings/issues/387_
