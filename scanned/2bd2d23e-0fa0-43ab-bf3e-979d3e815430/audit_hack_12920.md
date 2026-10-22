# [M] Function post_dca_order() use wrong value of max_slippage

## Summary
Severity: Medium
Reporter: SovaSlava
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L101
Type: audit-issue

## Details
# Function post_dca_order() use wrong value of max_slippage

## Summary
Function post_dca_order() use wrong value of max_slippage, because in order struct uses value from parameter.
## Vulnerability Detail
if value of parameter _max_slippage will be 0, in order struct will be stored value 0, instead of MAX_SLIPPAGE
```solidity
post_dca_order(...) 
...
 max_slippage: uint256 = _max_slippage
    if max_slippage == 0:
        max_slippage = MAX_SLIPPAGE
    
    order: DcaOrder = DcaOrder({
        uid: empty(bytes32),
        account: msg.sender,
        token_in: _token_in,
        token_out: _token_out,
        amount_in_per_execution: _amount_in_per_execution,
        seconds_between_executions: _seconds_between_executions,
        max_number_of_executions: _max_number_of_executions,
        // @audit-issue we use _max_slippage value instead of max_slippage
        max_slippage: _max_slippage,
        twap_length: _twap_length,
        number_of_executions: 0,
        last_execution: 0
    })
```
## Impact
User can lose money from frontrun/sandwich attack.
## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L101
## Tool used

Manual Review

## Recommendation
```solidity
max_slippage: max_slippage,
```
