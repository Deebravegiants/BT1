# [M] licenseFee can be greater than BASE

## Summary
Severity: Medium
Contest weight: 0.1055
Dataset id: 910
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Worst case - no functions that contains `handleFees()` can pass because [line 118](https://github.com/code-423n4/2021-09-defiProtocol/blob/main/contracts/contracts/Basket.sol#L118) will always underflow and revert. You only need `feePct` to be bigger than `BASE` for the `handleFees()` function to fail which will result in a lot of gas wasted and potentially bond burnt.

I did not classify this as high risk because a simple fix would be to simply reduce the licenseFee via `changeLicenseFee`.

## Recommendation
Add these require statement to the following functions:

* Basket.changeLicenseFee()
  * `require(newLicenseFee <= BASE, "changeLicenseFee: license fee cannot be greater than 100%");`
* Factory.proposeBasketLicense()
  * `require(licenseFee <= BASE, "proposeBasketLicense: license fee cannot be greater than 100%");`

Agree with the finding, the warden highlighted an admin exploit that allows to DOS the basket. Adding a check not only prevents the exploit, but gives a security guarantee to the protocol users
