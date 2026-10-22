# [M] Possible Sandwich/MEV Attacks For Drip Collection

## Summary
Severity: Medium
Contest weight: 0.4609
Dataset id: 12531
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As part of the incentive mechanisms, the Minterest protocol has the BuybackDripper that distributes a token to buyback at a defined drip rate. The participating user is entitled to receive pro-rata drip distribution based on the weight of the associated user account. Our analysis shows this mechanism may be abused to steal most drip distribution. To elaborate, we show below the drip() routine. As the name indicates, the function drips tokens to buyback with the defined drip rate. By design, it cannot be called more than once per hour. We notice this function is permissionless and open to public. Internally, it invokes the buyback() routine (line 94), which basically re-computes and saves the new shareAccMantissa state to record the accumulated reward index.
```solidity
function drip() external {
    uint256 timeUnits = getTime();
    uint256 timeSinceDrip = timeUnits - previousDripTime;
    require(timeSinceDrip > 0, ErrorCodes.TOO_EARLY_TO_DRIP);
    // Reset period if last drip was older than period duration
    if (timeSinceDrip >= periodDuration) {
        previousDripTime = timeUnits;
        resetPeriod(timeUnits);
        return;
    }
    uint256 nextPeriodStart = periodStart + periodDuration;
    uint256 dripUntil = Math.min(timeUnits, nextPeriodStart);
    uint256 dripDuration = dripUntil - previousDripTime;
    uint256 toDrip = dripDuration * dripPerHour;
    previousDripTime = dripUntil;
    if (dripUntil >= nextPeriodStart) {
        resetPeriod(nextPeriodStart);
    }
    buyback.buyback(toDrip);
}

function buyback(uint256 amount_) external onlyRole(DISTRIBUTOR) {
    require(amount_ > 0, ErrorCodes.NOTHING_TO_DISTRIBUTE);
    require(weightSum > 0, ErrorCodes.NOT_ENOUGH_PARTICIPATING_ACCOUNTS);
    uint256 shareMantissa = (amount_ * SHARE_SCALE) / weightSum;
    shareAccMantissa = shareAccMantissa + shareMantissa;
    emit NewBuyback(amount_, shareMantissa);
    mnt.safeTransferFrom(msg.sender, address(this), amount_);
}
```
With that, it is possible to have a sandwich scenario where a malicious actor may flash to borrow a large amount of asset to stake to increase the weight of a controlled account, then invoke the above open drip(), and next unstake and repay the flashloan. By doing so, the malicious actor may simply have the most share of the tokens that are just distributed via drip().

## Recommendation
Improve the above drip mechanism to ensure the user staked funds are locked for a certain period to thwart possible flashloan-assisted MEV attacks.
