# [M] Value can be stuck in Adapters

## Summary
Severity: Medium
Contest weight: 0.4142
Dataset id: 17063
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
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
            );
    }
```
Same code exists in LooksRareAdapter, SeaportAdapter, and X2Y2Adapter.

## Proof of Concept
matchAskWithTakerBid is payable, it calls `functionCallWithValue` with the value parameter. There are no checks to make sure `msg.value == value`, if excess value is sent user will not receive a refund.

## Recommendation
Check `msg.value == value`  
If the function is only supposed to be delegate called into, consider adding a check to prevent direct call.
