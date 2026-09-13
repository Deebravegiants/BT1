# [H] 7.1 Fees May Block Slow Path

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design High Version 1 Code Corrected

The slow path goes through L1DAIWormholeBridge.finalizeRegisterWormhole() which calls
requestMint with maxFee = 0.

When the vat is live, the computed fee in _withdraw function of WormholeJoin may be > 0 and the
transaction would revert due to:

```
require(fee <= maxFee, "WormholeJoin/max-fee-exceed");
```
This essentially prevents users who are censored by the oracle to redeem using the slow path.

Code corrected:

The only fee currently present, the WormholeConstantFee, now features a ttl after which the fee returned
for this WormholeGUID is 0.
