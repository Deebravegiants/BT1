# [H] matchOrder : depositted eth is not sent to  BullvsBear contract `(address(this))`

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-bullvbear
Published: 2022-11-21
Source: https://github.com/sherlock-audit/2022-11-bullvbear-judging/issues/79
Type: sherlock-finding

## Details
ak1

high

# matchOrder : depositted eth is not sent to  BullvsBear contract `(address(this))`

## Summary
When `matchOrder`, if amount is eth, it is [deposited ](WETH(weth).deposit{value: msg.value}();) . 
The weth is not sent to BullvsBear contract which could be used while settling the order.

## Vulnerability Detail

In `matchOrder` function, if user sent as ETH, then it is converted into weth and than should be deposited in the BullvsBear contract.

https://github.com/sherlock-audit/2022-11-bullvbear/blob/main/bvb-protocol/src/BvbProtocol.sol#L348-L355

But, when we see the above code flow, the deposited ETH is not sent to `address(this)`

## Impact

The bear will not receive the collateral amount during settlement.

## Code Snippet

https://github.com/sherlock-audit/2022-11-bullvbear/blob/main/bvb-protocol/src/BvbProtocol.sol#L348-L355

## Tool used

Manual Review

## Recommendation

After depsoiting the eth, transfer the weth to `address(this)`

        if (msg.value > 0) {
            require(msg.value == takerPrice, "INVALID_ETH_VALUE");
            require(order.asset == weth, "INCOMPATIBLE_ASSET_ETH_VALUE");


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-bullvbear-judging/issues/79_
