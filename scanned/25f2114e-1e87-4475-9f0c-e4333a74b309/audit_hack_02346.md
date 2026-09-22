# [M] \[M04\] Additive rounding errors

## Summary
Severity: Medium
Source: https://github.com/SetProtocol/set-protocol-v2/blob/b8286f431547823ff3935a1343cd4cf4d77585a1/contracts/protocol/lib/Position.sol#L141
Type: audit-issue

## Details
The [calculateDefaultEditPositionUnit](https://github.com/SetProtocol/set-protocol-v2/blob/b8286f431547823ff3935a1343cd4cf4d77585a1/contracts/protocol/lib/Position.sol#L141) determines the new position unit based on the change in the total notional component tokens held. However, using the change in position may incur excessive rounding errors, particularly if the change is small. Additionally, multiple small changes will cause these errors to accumulate. Consider calculating the new position unit directly using the `_postTotalNotional` and `_setTokenSupply` values.
