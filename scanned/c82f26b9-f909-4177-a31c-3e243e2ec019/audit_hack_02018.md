# [M] 7.3 Minting Pending DAI Incurs Additional Fees

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

Using the DAI Wormhole may take a fee from the user. This fee is taken on L1 and transferred to the
VOW. The fee is accounted for inside _withdraw() and calculated using an external Fee adapter
contract based on the wormholeGUID which contains all information about the transfer, the current debt
and the line, the debt ceiling according to the source domain.

The amount of the fee taken is calculated before determination of the amount that is withdrawn.

```
uint256 fee = vatLive? FeesLike(fees[wormholeGUID.sourceDomain]).getFees(wormholeGUID, line_, debt_) : 0;
require(fee <= maxFee, "WormholeJoin/max-fee-exceed");
uint256 amtToTake = _min(
pending,
uint256(int256(line_) - debt_)
);
```
The fee is based on the full amount of the wormholeGUID being processed, not on the actual amount
withdrawn in this transaction. The actual amount withdrawn is limited by the maximum debt that can be
created without exceeding the ceiling. The remaining amount can be retrieved later when more debt can
be accrued using mintPending(). This however again uses function _withdraw which again
calculates the fee based on the full amount of the wormholeGUID, the current debt and debt ceiling. The
pending amount is not taken into account for the calculation of the fee.

Hence, should the amount to be withdrawn be limited by the remaining space between the debt ceiling
(line) and the current debt, the user pays fees based on the full amount, not the amount being withdrawn.
Later, when the remaining pending amount is withdrawn, the user again pays fees based on the full
amount of the wormholeGUID, effectively paying again for the same transfer.

Code corrected:

The fee computation function getFee takes more parameters (pending, amtToTake) into account. This
allows more versatile ways to compute the fee. For example, WormholeConstantFee can now
compute the fee relative to the amount being withdrawn instead of the full fee every time the full amount
is partially withdrawn.
