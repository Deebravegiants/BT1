# [M] `_storeRebase

## Summary
Severity: Medium
Contest weight: 0.1845
Dataset id: 13355
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`_storeRebase()`’s signature is as such:

  * [Yieldy.sol#_storeRebase()](https://github.com/code-423n4/2022-06-yieldy/blob/524f3b83522125fb7d4677fa7a7e5ba5a2c0fe67/src/contracts/Yieldy.sol#L110-L114)

    File: Yieldy.sol
    104:     /**
    105:         @notice emits event with data about rebase
    106:         @param _previousCirculating uint
    107:         @param _profit uint
    108:         @param _epoch uint
    109:      */
    110:     function _storeRebase(
    111:         uint256 _previousCirculating,
    112:         uint256 _profit,
    113:         uint256 _epoch
    114:     ) internal {

However, instead of being called with the expected `_previousCirculating` value, it’s called with the current circulation value:

  * [Yieldy.sol#rebase()](https://github.com/code-423n4/2022-06-yieldy/blob/524f3b83522125fb7d4677fa7a7e5ba5a2c0fe67/src/contracts/Yieldy.sol#L97-L100)

    File: Yieldy.sol
    89:             uint256 updatedTotalSupply = currentTotalSupply + _profit;
    ...
    103:             _totalSupply = updatedTotalSupply;
    104: 
    105:             _storeRebase(updatedTotalSupply, _profit, _epoch); // @audit-info this should be currentTotalSupply otherwise previous = current

As a consequence, the functionality isn’t doing what it was created for.

## Recommendation
Consider calling `_storeRebase()` with `currentTotalSupply`:

    File: Yieldy.sol
    - 105:             _storeRebase(updatedTotalSupply, _profit, _epoch);
    + 105:             _storeRebase(currentTotalSupply, _profit, _epoch);
