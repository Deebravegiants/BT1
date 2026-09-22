# [H] 6.1 Solv Issuer Double Accounting

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness High Version 1 Code Corrected

The Solv Issuer external position keeps track of the offered vouchers on the convertible offering
marketplace. To compute their values it sums up

```
1.The token amounts that could be withdrawn by the issuer with internal function
__getWithdrawableAssetAmounts.
2.The token amounts that could be claimed in case some units are still held with internal function
__getOffersUnderlyingBalance()
```
```
3.The unreconciled token amounts.
```
__getWithdrawableAssetAmounts() iterates over all offers and further iterates over all issuer slots
of the external position. There is a possibility of accounting withdrawable amounts multiple times.

```
for (uint256 i; i < offersLength; i++) {
// ...
ISolvV2ConvertibleVoucher voucherContract = ISolvV2ConvertibleVoucher(
INITIAL_CONVERTIBLE_OFFERING_MARKET_CONTRACT.offerings(_offers[i].offerId).voucher
);
ISolvV2ConvertiblePool voucherPoolContract = ISolvV2ConvertiblePool(
voucherContract.convertiblePool()
);
uint256[] memory slots = voucherPoolContract.getIssuerSlots(address(this));
// ...
```

```
for (uint256 j; j < slotsLength; j++) {
(uint256 withdrawCurrencyAmount, uint256 withdrawTokenAmount) = voucherPoolContract
.getWithdrawableAmount(slots[j]);
// logic for summing up
// ...
```
Consider the following example:

```
1.First offer is created with the voucher being X such that it has slot id 1.
2.Second offer is created with the voucher being X such that it has slot id 2.
3.The above code is executed.
4.The convertible pool of the voucher gives the slots 1 and 2.
5.The withdrawable amount is added twice since the inner loop for both offers will iterate over slot ids
1 and 2 and add the withdrawable amounts twice.
```
Ultimately, the withdrawable amounts may be added multiple times in the evaluation.

Code corrected:

Now, not only offers are tracked but also issued voucher addresses. Hence, estimating the withdrawable
amounts is done by iterating now over the issued voucher addresses which do not contain duplicates.
