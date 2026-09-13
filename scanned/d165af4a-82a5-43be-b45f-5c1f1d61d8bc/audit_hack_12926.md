# [M] Dca orders may fail due to zero slippage

## Summary
Severity: Medium
Reporter: evilakela
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L119C1-L121
Type: audit-issue

## Details
# Dca orders may fail due to zero slippage

## Summary
`Dca.post_dca_order` not setting slippage to `MAX_SLIPPAGE` constant if `_max_slippage=0`, but pretending to do so. If this is design decision - set `MAX_SLIPPAGE` as slippage if user for some reason don't want to set it, it fails to do that and such orders will fail.

## Vulnerability Detail
DcaOrder struct use `_max_slippage`, not `max_slippage`
```vyper
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
        max_slippage: _max_slippage, # <- use max_slippage here
        twap_length: _twap_length,
        number_of_executions: 0,
        last_execution: 0
    })
```

## Impact
Orders where user not set `_max_slippage` will fail due to unrealistic zero slippage expectation

## Code Snippet
[https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L119C1-L121
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L131](https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L119-L135)

## Tool used
Manual Review

## Recommendation
`DcaOrder({
    ...
    max_slippage: max_slippage
    ...
})`
