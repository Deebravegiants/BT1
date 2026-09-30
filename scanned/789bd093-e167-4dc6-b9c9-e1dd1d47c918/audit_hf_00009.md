# [M] Proper Refund of The Excess ETH

## Summary
Severity: Medium
Contest weight: 0.4491
Dataset id: 39
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In DarkCrypto, there is a contract TaxOffice which provides a number of convenience routines for liquidation addition, e.g., addLiquidityTaxFree() and addLiquidityETHTaxFree(). During the analysis of these convenience routines, we notice that addLiquidityETHTaxFree() does not refund the excess ETH properly. To elaborate, we show below the implementation of addLiquidityTaxFree(). This routine receives ETH and tokens from the caller, provides them to the uniRouter to add liquidity. The uniRouter should refund the excess ETH to the TaxOffice contract.
```solidity
function addLiquidityETHTaxFree(
    uint256 amtDark,
    uint256 amtDarkMin,
    uint256 amtFtmMin
)
    external
    payable
    returns (
        uint256,
        uint256,
        uint256
    )
{
    require(amtDark != 0 && msg.value != 0, "amounts can t be 0");
    _excludeAddressFromTax(msg.sender);
    IERC20(dark).transferFrom(msg.sender, address(this), amtDark);
    _approveTokenIfNeeded(dark, uniRouter);
    _includeAddressInTax(msg.sender);
    uint256 resultAmtDark;
    uint256 resultAmtFtm;
    uint256 liquidity;
    (resultAmtDark, resultAmtFtm, liquidity) = IUniswapV2Router(uniRouter)
        .addLiquidityETH{value: msg.value}(
            dark,
            amtDark,
            amtDarkMin,
            amtFtmMin,
            msg.sender,
            block.timestamp
        );
    if (amtDark.sub(resultAmtDark) > 0) {
        IERC20(dark).transfer(msg.sender, amtDark.sub(resultAmtDark));
    }
    return (resultAmtDark, resultAmtFtm, liquidity);
}
```
However, it comes to our attention that in the current implementation, the excess ETH returned from the router to the TaxOffice contract is not sent back to the caller. This will cause msg.value - resultAmtFtm amount of ETH left in the contract.

## Recommendation
Revise the above routine to properly return the excess ETH back to the user.
