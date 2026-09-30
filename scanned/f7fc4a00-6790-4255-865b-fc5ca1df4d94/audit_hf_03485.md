# [H] `multiHopSellCollateral` can fail due to non-existent market on destination chain

## Summary
Severity: High
Contest weight: 0.6805
Dataset id: 19069
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`multiHopSellCollateral()` allows users to leverage down by selling the `TOFT` collateral on another chain and then send it to host chain (Arbitrum) for repayment of USDO loan.

However, it will fail as it tries to obtain the `repayableAmount` on the destination chain by calling `IMagnetar.getBorrowPartForAmount()` on a non-existing market. That is because Singularity/BigBang markets are only deployed on the host chain.

```solidity
function leverageDownInternal(
    uint256 amount,
    IUSDOBase.ILeverageSwapData memory swapData,
    IUSDOBase.ILeverageExternalContractsData memory externalData,
    IUSDOBase.ILeverageLZData memory lzData,
    address leverageFor
) public payable {
    _unwrap(address(this), amount);

    //swap to USDO
    IERC20(erc20).approve(externalData.swapper, amount);
    ISwapper.SwapData memory _swapperData = ISwapper(externalData.swapper)
        .buildSwapData(erc20, swapData.tokenOut, amount, 0, false, false);
    (uint256 amountOut, ) = ISwapper(externalData.swapper).swap(
        _swapperData,
        swapData.amountOutMin,
        address(this),
        swapData.data
    );

    // @audit this call will fail as there is no market in destination chain
    // repay
    uint256 repayableAmount = IMagnetar(externalData.magnetar)
        .getBorrowPartForAmount(externalData.srcMarket, amountOut);
```

## Proof of Concept
Consider the following scenario where a user leverage down by selling the collateral on Ethereum (a non-host chain).

1. User first triggers `Singularity.multiHopSellCollateral()` on host chain Arbitrum.
2. That will call `SGLLeverage.multiHopSellCollateral()`, which will conduct a cross chain message via `ITapiocaOFT(address(collateral)).sendForLeverage()` to bridge over and sell the collateral on Ethereum mainnet.
3. The collateral TOFT contract on Ethereum mainnet will receive the bridged collateral and cross-chain message via `_nonBlockingLzReceive()` and then `BaseTOFTLeverageModule.leverageDown()`.
4. The execution continues with `BaseTOFTLeverageModule.leverageDownInternal()`, but it will revert as it attempt to call `getBorrowPartForAmount()` for a non-existing market in Ethereum.
5. The bridged collateral will be locked in the TOFT contract on Ethereum mainnet as the refund mechanism will also revert and `retryMessage()` will continue to fail as this is a permanent error.

## Recommendation
Obtain the repayable amount on the Arbitrum (host chain) where the BigBang/Singularity markets are deployed.
