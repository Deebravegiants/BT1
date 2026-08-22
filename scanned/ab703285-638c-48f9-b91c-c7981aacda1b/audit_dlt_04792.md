# [M] M-03 Blockhash doesn't work for current block

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-mover
Published: 2022-10-28
Source: https://github.com/sherlock-audit/2022-10-mover-judging/issues/50
Type: sherlock-finding

## Details
GalloDaSballo

medium

# M-03 Blockhash doesn't work for current block

## Summary

https://github.com/sherlock-audit/2022-10-mover/blob/main/cardtopup_contract/contracts/HardenedTopupProxy.sol#L1058-L1059

Should check that block provided is less than current as the current blockHash cannot be known

## Vulnerability Detail

Checking for blockhash(block.number) will always return 0

## Impact

Am not sure value can be stolen via this

## Code Snippet

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

contract MoverTests {
  function prooveBlockhash(uint256 blockNumberDelta, bytes32 expected) external {
    uint256 blockTarget = block.number - blockNumberDelta;
    require(expected == blockhash(blockTarget), "Hash is not expected");
  }
}
```

If the value was non-zero we'd get a revert

```python
>>> c.prooveBlockhash(0, 0, {"from": a[0]})
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-mover-judging/issues/50_
