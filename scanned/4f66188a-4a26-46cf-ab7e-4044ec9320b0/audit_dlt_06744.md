# [M] Value can be stuck in Adapters

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-paraspace
Published: 2022-12-08
Source: https://github.com/code-423n4/2022-11-paraspace-findings/issues/215
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-11-paraspace/blob/c6820a279c64a299a783955749fdc977de8f0449/paraspace-core/contracts/misc/marketplaces/LooksRareAdapter.sol#L73-L94
https://github.com/code-423n4/2022-11-paraspace/blob/c6820a279c64a299a783955749fdc977de8f0449/paraspace-core/contracts/misc/marketplaces/SeaportAdapter.sol#L93-L107
https://github.com/code-423n4/2022-11-paraspace/blob/c6820a279c64a299a783955749fdc977de8f0449/paraspace-core/contracts/misc/marketplaces/X2Y2Adapter.sol#L88-L102


# Vulnerability details

## Impact

matchAskWithTakerBid is payable, it call `functionCallWithValue` with the `value parameter. There are no check to make sure `msg.value == value`, if excess value is sent user will not receive a refund.

## Proof of Concept

https://github.com/code-423n4/2022-11-paraspace/blob/c6820a279c64a299a783955749fdc977de8f0449/paraspace-core/contracts/misc/marketplaces/LooksRareAdapter.sol#L73-L94

```solidity
    function matchAskWithTakerBid(
        address marketplace,
        bytes calldata params,
        uint256 value
    ) external payable override returns (bytes memory) {
        bytes4 selector;
        if (value == 0) {
            selector = ILooksRareExchange.matchAskWithTakerBid.selector;
        } else {
            selector = ILooksRareExchange
                .matchAskWithTakerBidUsingETHAndWETH
                .selector;
        }
        bytes memory data = abi.encodePacked(selector, params);
        return
            Address.functionCallWithValue(
                marketplace,
                data,
                value,
                Errors.CALL_MARKETPLACE_FAILED
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-11-paraspace-findings/issues/215_
