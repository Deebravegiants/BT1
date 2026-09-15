# [M] Dca: TWAP contract does not exist on arbitrum

## Summary
Severity: Medium
Reporter: n33k
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L49
Type: audit-issue

## Details
# Dca: TWAP contract does not exist on arbitrum

## Summary

TWAP address `0xFa64f316e627aD8360de2476aF0dD9250018CFc5` is not a contract on arbitrum.

## Vulnerability Detail

```python
TWAP: constant(address) = 0xFa64f316e627aD8360de2476aF0dD9250018CFc5 
```

View it on arbiscan. It's an EOA.

https://arbiscan.io/address/0xFa64f316e627aD8360de2476aF0dD9250018CFc5

## Impact

`_calc_min_amount_out` does not work.

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L49

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L268

## Tool used

Manual Review

## Recommendation

None.
