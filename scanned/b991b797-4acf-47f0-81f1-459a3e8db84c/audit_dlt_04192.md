# [M] DODORouteProxy.sol#L475 : when broker address is not set, fee amount will be lost.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/79
Type: sherlock-finding

## Details
ak1

medium

# DODORouteProxy.sol#L475 : when broker address is not set, fee amount will be lost.

## Summary
Inside the function `_routeWithdraw`, fees are collected.
`routeFee` is sent to `routeFeeReceiver` and `brokerFee` is sent to `broker`

The contract has enough check to validate the `routeFeeReceiver` address. Refer the constructor where it has validation check.
        
        constructor(address payable weth, address dodoApproveProxy, address feeReceiver) public {
        require(feeReceiver != address(0), "DODORouteProxy: feeReceiver invalid");

But, there is no validation whether the `broker` address is valid or not. if it is not set, then the broker fee could be sent to either incorrect address or invalid address. once the fee sent to invalid/incorrect address, it never be ragained.

## Vulnerability Detail

https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L475-L482

In above line of codes, it is clear that the broker address is get from decode data and it is not validated.

## Impact
If fee is sent invalid address, it never be regained.
consistency is missing in validating the fee receiver addresses. 

## Code Snippet

https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L475-L482

## Tool used

Manual Review

## Recommendation
check whether the `broker` is valid or not inside the `_routeWithdraw`
