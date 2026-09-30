# [H] Can not update target price

## Summary
Severity: High
Contest weight: 0.3257
Dataset id: 1084
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The sanity checks in `rampTargetPrice` are broken [SwapUtils.sol#L1571-L1581](https://github.com/code-423n4/2021-11-bootfinance/blob/main/customswap/contracts/SwapUtils.sol#L1571-L1581)
    
        if (futureTargetPricePrecise < initialTargetPricePrecise) {
            require(
                futureTargetPricePrecise.mul(MAX_RELATIVE_PRICE_CHANGE).div(WEI_UNIT) >= initialTargetPricePrecise,
                "futureTargetPrice_ is too small"
            );
        } else {
            require(
                futureTargetPricePrecise <= initialTargetPricePrecise.mul(MAX_RELATIVE_PRICE_CHANGE).div(WEI_UNIT),
                "futureTargetPrice_ is too large"
            );
        }

If `futureTargetPricePrecise` is smaller than `initialTargetPricePrecise` 0.01 of `futureTargetPricePrecise` would never larger than `initialTargetPricePrecise`.

Admin would not be able to ramp the target price. As it’s one of the most important features of the customswap, I consider this is a high-risk issue

## Proof of Concept
Here’s a web3.py script to demo that it’s not possible to change the target price even by 1 wei.
    
    p1, p2, _, _ =swap.functions.targetPriceStorage().call()
    future = w3.eth.getBlock(w3.eth.block_number)['timestamp'] + 200 * 24 * 3600

## Recommendation
Would it be something like:
    
        if (futureTargetPricePrecise < initialTargetPricePrecise) {
            require(
                futureTargetPricePrecise.mul(MAX_RELATIVE_PRICE_CHANGE + WEI_UNIT).div(WEI_UNIT) >= initialTargetPricePrecise,
                "futureTargetPrice_ is too small"
            );
        } else {
            require(
                futureTargetPricePrecise <= initialTargetPricePrecise.mul(MAX_RELATIVE_PRICE_CHANGE + WEI_UNIT).div(WEI_UNIT),
                "futureTargetPrice_ is too large"
            );
        }

I believe the dev would spot this mistake if there’s a more relaxed timeline.
