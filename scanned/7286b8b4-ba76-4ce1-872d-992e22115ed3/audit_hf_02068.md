# [M] Possible Sandwich/MEV Attacks For Reduced Returns

## Summary
Severity: Medium
Contest weight: 0.4608
Dataset id: 11728
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function addLiquidity()
external
onlyGov
nonReentrant
{
    require(!isLiquidityAdded, "Treasury: liquidity already added");
    isLiquidityAdded = true;
    uint256 busdAmount = busdReceived.mul(busdBasisPoints).div(BASIS_POINTS_DIVISOR);
    uint256 gmtAmount = busdAmount.mul(PRECISION).div(gmtListingPrice);
    IERC20(busd).approve(router, busdAmount);
    IERC20(gmt).approve(router, gmtAmount);
    IGMT(gmt).endMigration();
    IPancakeRouter(router).addLiquidity(
        busd, // tokenA
        gmt, // tokenB
        busdAmount, // amountADesired
        gmtAmount, // amountBDesired
        0, // amountAMin
        0, // amountBMin
        address(this), // to
        block.timestamp // deadline
    );
    IGMT(gmt).beginMigration();
    uint256 fundAmount = busdReceived.sub(busdAmount);
    IERC20(busd).transfer(fund, fundAmount);
```

To elaborate, we show above the related addLiquidity() routine. We notice it is routed to UniswapV2-like router in order to provide the desired liquidity. Apparently, the instant DEX price for liquidity addition is highly volatile and there is a need to consider the use of TWAP and further specify necessary restriction on possible slippage, so that it is not vulnerable to possible front-running attacks. Note that this is a common issue plaguing current AMM-based DEX solutions. Specifically, a large trade may be sandwiched by a preceding sell to reduce the market price, and a tailgating buy-back of the same amount plus the trade amount. Such sandwiching behavior unfortunately causes a loss and brings a smaller return as expected to the trading user because the swap rate is lowered by the preceding sell. As a mitigation, we may consider specifying the restriction on possible slippage caused by the trade or referencing the TWAP or time-weighted average price of UniswapV2. Nevertheless, we need to acknowledge that this is largely inherent to current blockchain infrastructure and there is still a need to continue the search efforts for an effective defense.

## Recommendation
Develop an effective mitigation (e.g., slippage control) to the above front-running attack to better protect the interests of farming users.
