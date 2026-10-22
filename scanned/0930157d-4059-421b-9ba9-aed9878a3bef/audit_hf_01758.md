# [M] Check slippage of swaps

## Summary
Severity: Medium
Contest weight: 0.3885
Dataset id: 9654
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Several bridges check that the output of swaps isn’t 0. However it could also happen that swap give a positive output, but still lower than expected due to slippage / sandwiching / MEV. Several AMMs will have a mechanism to limit slippage, but it might be useful to add a generic mechanism as multiple swaps in sequence might have a relative large slippage.
```solidity
function swapAndStartBridgeTokensViaOmniBridge(...) ... {
    ...
    uint256 amount = _executeAndCheckSwaps(_lifiData, _swapData, payable(msg.sender));
    if (amount == 0) {
        revert InvalidAmount();
    }
    _startBridge(_lifiData, _bridgeData, amount, true);
}
```

## Recommendation
Consider adding a slippage check by specifying a minimum amount of expected tokens.
At least add a check for amount==0 in all bridges.
