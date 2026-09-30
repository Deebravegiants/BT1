# [M] 6.3 Offer ID and Voucher Mismatch

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

When buying an offer from the Solv IVO, the fund manager can specify the voucher address and the
offering ID. However, the voucher address could mismatch with the offer's voucher stored in the
Offering struct.

Consider the following scenario:

```
1.Fund manager inputs an offer id such that Offer.voucher and the input voucher mismatch.
```

```
2.The SolvV2ConvertibleBuyerPositionParser specifies Offer.currency as the asset to transfer
while specifying the amount to transfer as
```
```
uint256 amount = uint256(units).mul(voucherPrice).div(10**uint256(market.decimals));
```
```
3.The nextTokenId() is queried on the wrong voucher and the contract maximum approval is
given to the IVO market.
4.buy() is called on the IVO market. As long as the amount computed in step 2. is sufficient, buying
will succeed.
5.The approval is revoked.
6.The input voucher and the token id from step 3 are pushed on the position's offers array.
```
While it requires an error by the fund manager, it could have consequences such as

- tracking of a wrong voucher and token id leading to wrong estimations of the total value,
- stuck tokens due to high amounts being moved also leading to wrong fund evaluations,
- being stuck with the wrong voucher and token id
- potential of double tracking of voucher and token id

Ultimately, to buy an offering it could be sufficient to specify solely the units and the offering id.

Code corrected:

The voucher address is not an action argument anymore for buying from IVOs but is retrieved from the
offering. Hence, the position parser and the position logic have been adapted accordingly.
