# [M] Wrong events for critical parameter changes

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-opyn
Published: 2022-12-03
Source: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/194
Type: sherlock-finding

## Details
hansfriese

medium

# Wrong events for critical parameter changes

## Summary

Function `setOTCPriceTolerance` is used to set the critical parameter `otcPriceTolerance` but a wrong event is emitted when there is a change. This can confuse users and lead to unintended results affecting the protocol's reputation.

## Vulnerability Detail

`otcPriceTolerance` is a critical parameter that prevents an operator to do netting with a wrong price and I believe the users are sensitive to this because they deposit/queue requests without specifying kind of minimum out amount.
But in the admin setter function(CrabNetting.sol#L744), a wrong event is emitted and this will confuse users and can lead to unintended results.

```solidity
function setOTCPriceTolerance(uint256 _otcPriceTolerance) external onlyOwner {
    // Tolerance cannot be more than 20%
    require(_otcPriceTolerance <= MAX_OTC_PRICE_TOLERANCE, "Price tolerance has to be less than 20%");
    uint256 previousOtcTolerance = auctionTwapPeriod; //@audit should be previousOtcTolerance = otcPriceTolerance

    otcPriceTolerance = _otcPriceTolerance;

    emit SetOTCPriceTolerance(previousOtcTolerance, _otcPriceTolerance);
}
```

Other than this, there is another place (CrabNetting.sol#L413) where a wrong event is emitted (wrong withdraw amount) that will affect the off-chain tracking of user withdraw queue.

```solidity
function netAtPrice(uint256 _price, uint256 _quantity) external onlyOwner {
    ...
    // process withdraws and send usdc
    i = withdrawsIndex;
    while (crabQuantity > 0) {
        Receipt memory withdraw = withdraws[i];
        if (withdraw.amount == 0) {
            i++;
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/194_
