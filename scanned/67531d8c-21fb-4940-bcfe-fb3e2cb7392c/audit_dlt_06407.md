# [H] dynamicFeeBps is assymetric

## Summary
Severity: High
Chain: Smart contract
Component: Origami
Published: 2024-02-22
Source: https://github.com/hats-finance/Origami-0x998f1b716a5022be026ca6b919c0ddf45ca31abd/issues/9
Type: hats-finding

## Details
**Github username:** @0xLogos
**Twitter username:** --
**Submission hash (on-chain):** 0x6bea734e2375c9a608bf88f289905faf591b9c20978f96e7d83eb5a572c4b92a
**Severity:** high

**Description:**
In DynamicFees library price relative diff calculated as `delta / _histPrice` and multipled by leverage factor to obtain final fee.

Here is how `delta` calculated:

```
// _inQuotedOrder = true for base/quote oracle and false for quote/base oracle
uint256 _delta;
if (feeType == FeeType.DEPOSIT_FEE) {
    unchecked {
        if (_inQuotedOrder && _spotPrice < _histPrice) {
            _delta = _histPrice - _spotPrice; // case 1
        } else if (!_inQuotedOrder && _spotPrice > _histPrice) {
            _delta = _spotPrice - _histPrice; // case 2
        }
    }
} else {
    unchecked {
        if (_inQuotedOrder && _spotPrice > _histPrice) {
            _delta = _spotPrice - _histPrice; // case 2
        } else if (!_inQuotedOrder && _spotPrice < _histPrice) {
            _delta = _histPrice - _spotPrice; // case 1
        }
    }
}
```

There is 2 cases
1. `spot > hist, delta = spot - hist, diff = (spot - hist) / hist = spot/hist - 1`
2. `spot < hist, delta = hist - spot, diff = (hist - spot) / hist = 1 - spot/hist`

In fist case when spot price increases => spot/hist ration increases to infinity => multiplier increases to infinity.
But in 2 case spot when price decreases => spot/hist ratio decreases => multiplier increases to 1 at max

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Origami-0x998f1b716a5022be026ca6b919c0ddf45ca31abd/issues/9_
