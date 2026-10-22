# [H] The Variable maxscale Is Not Saved

## Summary
Severity: High
Contest weight: 0.8612
Dataset id: 15005
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Situation:
In the function _collect() of Divider.sol, the value maxscale is updated in a temporary variable. However, this temporary variable is not written back to its origin. This means the value of maxscale is not kept over time.
```solidity
function _collect(...) internal returns (uint256 collected) {
    ...
    Series memory _series = series[adapter][maturity];
    ...
    // If this is larger than the largest scale we've seen for this Series, use it
    if (cscale > _series.maxscale) {
        // _series is a local variable
        _series.maxscale = cscale;
        lscales[adapter][maturity][usr] = cscale;
    // If not, use the previously noted max scale value
    } else {
        lscales[adapter][maturity][usr] = _series.maxscale;
    }
} // _series is not saved to series[adapter][maturity]
```

## Recommendation
Do one of the following:
• Replace memory with storage. This way any access to _series translates to sload/sstore.
```solidity
Series storage _series = series[adapter][maturity];
```
• At the end of function _collect(), add the following to "save" the value of _series.maxscale. This is assuming maxscale is the only part that has to be saved.
```solidity
series[adapter][maturity].maxscale = _series.maxscale;
```
