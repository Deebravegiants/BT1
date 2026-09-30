# [M] _cleanup_order doesn't update allowance to 0

## Summary
Severity: Medium
Reporter: mahdiRostami
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L215-L229
Type: audit-issue

## Details
# _cleanup_order doesn't update allowance to 0

## Summary
a smart contract doesn't have to have an additional allowance 
## Vulnerability Detail
If the trader cancels the order or the order is canceled during execution.
Contract clean order in  _cleanup_order function, but allowance doesn't update.
## Impact
additional allowance to contract, which is inappropriate.
## Code Snippet
[https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L215-L229](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L215-L229)
[https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L300-L314](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L300-L314)
## Tool used

Manual Review

## Recommendation
update allowance in cleanup
