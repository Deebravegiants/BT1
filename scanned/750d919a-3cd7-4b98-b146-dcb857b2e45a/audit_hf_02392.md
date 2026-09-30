# [M] Potential Front-Running/MEV With Reduced Returns

## Summary
Severity: Medium
Contest weight: 0.4608
Dataset id: 12896
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The ReactorFusion protocol provides a RewardDistributor contract that basically distributes available rewards. The reward distribution involves the token swaps from USDC to WETH, and then to RF. With that, the protocol has provided a helper routine to facilitate the asset conversion: reap()
```solidity
function reap() public nonReentrant returns (uint256, uint256) {
    if (lastReap == block.timestamp) return (0, 0);
    require(msg.sender == address(underlying), "only underlying");
    // hardcoded to save gas
    IERC20 usdc = IERC20(0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4);
    CToken ceth = CToken(0xC5db68F30D21cBe0C9Eac7BE5eA83468d69297e6);
    CToken cusdc = CToken(0x04e9Db37d8EA0760072e1aCE3F2A219988Fdac29);
    IPair ethrf = IPair(0x62eB02CB53673b5855f2C0Ea4B8fE198901F34Ac);
    IPair usdceth = IPair(0xcd52cbc975fbB802F82A1F92112b1250b5a997Df);
    uint256 vc_delta;
    uint256 vcBal = vc.balanceOf(address(this));
    uint256 rf_delta;
    if (block.timestamp - lastGaugeClaim >= duration) {
        rf_delta = swappedRF;
        swappedRF = 0;
        ceth.takeReserves();
        cusdc.takeReserves();
        uint256 wethTotal = 0;
        uint256 usdcbal = usdc.balanceOf(address(this));
        uint256 usdcWethOut = usdceth.getAmountOut(usdcbal, address(usdc));
        if (usdcWethOut > 0) {
            usdc.transfer(address(usdceth), usdcbal);
            usdceth.swap(0, usdcWethOut, address(ethrf), "");
            wethTotal = usdcWethOut;
        }
    }
}
```
Public
To elaborate, we show above this helper routine. We notice the conversion is routed to UniswapV2-like pair in order to swap one asset to another. And the swap operation does not specify any restriction on possible slippage and is therefore vulnerable to possible front-running attacks, resulting in a smaller gain for this round of conversion. Note that this is a common issue plaguing current AMM-based DEX solutions. Speciﬁcally, a large trade may be sandwiched by a preceding sell to reduce the market price, and a tailgating buy-back of the same amount plus the trade amount. Such sandwiching behavior unfortunately causes a loss and brings a smaller return as expected to the trading user because the swap rate is lowered by the preceding sell. As a mitigation, we may consider specifying the restriction on possible slippage caused by the trade or referencing the TWAP or time-weighted average price of UniswapV2. Nevertheless, we need to acknowledge that this is largely inherent to current blockchain infrastructure and there is still a need to continue the search eﬀorts for an eﬀective defense.

## Recommendation
Develop an eﬀective mitigation (e.g., slippage control) to the above front-running attack to better protect the interests of farming users.
