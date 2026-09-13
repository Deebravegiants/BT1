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
(https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L159)

```solidity
//https://github.com/sushiswap/trident/blob/master/contracts/TridentRouter.sol
    function exactInputSingle(ExactInputSingleParams calldata params) public payable returns (uint256 amountOut) {
        // Prefund the pool with token A.
//@audit this modifies bento shares balances, not the actual inputToken balance
|>      bento.transfer(params.tokenIn, msg.sender, params.pool, params.amountIn);
        // Trigger the swap in the pool.
        amountOut = IPool(params.pool).swap(params.data);
        // Ensure that the slippage wasn't too much. This assumes that the pool is honest.
        if (amountOut < params.amountOutMinimum) revert TooLittleReceived();
    }
```
```solidity
//https://etherscan.io/address/0xf5bce5077908a1b7370b9ae04adc565ebd643966#code
//@audit allowed(from) modifier will check approval allowance for caller to manage bento shares, in this case, caller will be TridentRouter, and from will be ZetaTokenConsumerTrident.strategy.sol. 
    function transfer(
        IERC20 token,
        address from,
        address to,
        uint256 share
    ) public allowed(from) {
        // Checks
        require(to != address(0), "BentoBox: to not set"); // To avoid a bad UI from burning funds

        // Effects
|>      balanceOf[token][from] = balanceOf[token][from].sub(share);
        balanceOf[token][to] = balanceOf[token][to].add(share);

        emit LogTransfer(token, from, to, share);
    }
```
As seen above, tridentRouter.exactInputSingle() will try to modify bento shares of inputToken, instead of the actual raw erc-20, causing the transaction to revert.
Any transactions or flows that involve `getZetaFromToken()` will fail.

## Tools Used
Manual Review

## Recommended Mitigation Steps
In `ZetaTokenConsumerTrident.strategy.sol` `getZetaFromToken()`, use `tridentRouter.exactInputSingleWithNativeToken()` instead, which is designed to handle raw ERC-20 token and will deposit into Bento on behalf of `ZetaTokenConsumerTrident.strategy` first and then perform the swap.






## Assessed type

Error
