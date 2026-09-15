# [C] \[C02\] Fees are wrongly calculated

## Summary
Severity: Critical
Source: https://github.com/endaoment/endaoment-contracts/blob/f60aa253d3d869ad6460877f23e6092acb313add/contracts/Fund.sol#L119
Type: audit-issue

## Details
**Update:** _Partially fixed in [pull request #64](https://github.com/endaoment/endaoment-contracts/pull/64). Fees can be still evaluated to `0` but the Endaoment team acknowledged this, given the fact that it’s an uncommon outcome and that `grant` values are bounded by the web application._

In the [finalizeGrant](https://github.com/endaoment/endaoment-contracts/blob/f60aa253d3d869ad6460877f23e6092acb313add/contracts/Fund.sol#L119) function of the `Fund` contract, the `fee` parameter is calculated as `grant.value/100`. The entire system assumes that fees are paid to the admin of the fund whenever a grant is finalized.

Due to the [Solidity truncating rule for division](https://solidity.readthedocs.io/en/latest/types.html#division), if `grant.value < 100`, then `fee` will be zero and nothing will be paid to the `admin`.

The rounding error introduced when dividing will always round down the fees paid to the `admin`.

Consider handling the rounding errors using a library for decimals or introducing specific logic to handle them. Moreover, consider calculating the `finalGrant` variable as the `grant.value - fee`. This would make consistent the fact that both, if summed up, equal the `grant.value`.
