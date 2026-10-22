# [H] `ReferralFeePoolV0.sol#claimRewardAsMochi

## Summary
Severity: High
Contest weight: 0.2239
Dataset id: 1021
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[`ReferralFeePoolV0.sol#L28` L42](https://github.com/code-423n4/2021-10-mochi/blob/8458209a52565875d8b2cefcb611c477cefb9253/projects/mochi-core/contracts/feePool/ReferralFeePoolV0.sol#L28-L42)
    
    function claimRewardAsMochi() external {
        IUSDM usdm = engine.usdm();
        address[] memory path = new address[](2);
        path[0] = address(usdm);
        path[1] = uniswapRouter.WETH();
        path[2] = address(engine.mochi());
        usdm.approve(address(uniswapRouter), reward[msg.sender]);
        // we are going to ingore the slippages here
        uniswapRouter.swapExactTokensForTokens(
            reward[msg.sender],
            1,
            path,
            address(this),
            type(uint256).max
        );

In `ReferralFeePoolV0.sol#claimRewardAsMochi()`, `path` is defined as an array of length 2 while it should be length 3.

As a result, at L33, an out-of-bound exception will be thrown and revert the transaction.

## Recommendation
No recommendation
