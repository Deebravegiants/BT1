# [M] `multiHopSell` and `multiHopBuy` can be frontrunned with high slippage tolerance

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1368
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tapiocaz-audit/blob/bcf61f79464cfdc0484aa272f9f6e28d5de36a8f/contracts/tOFT/modules/BaseTOFTLeverageModule.sol#L111-L146


# Vulnerability details

## Impact
`multiHopSell` and `multiHopBuy` can be frontrunned with high slippage tolerance. User may experince loss from a sandwich attack.

## Proof of Concept
When a user initiates a cross chain request to `multiHopSell`, they need to sign a EIP712 permit to approve borrow share for TOFT contract. Attacker can take the signature and frontrun the tx with same data except a lower `swapData.amountOutMin`.

Action flow is multiHopSell(local) -> leverageDown(local) -> lend(remote)

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

As a result, user may experince loss from a sandwich attack. The attack applies to `multiHopBuy` in a similar way.

## Tools Used

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1368_
