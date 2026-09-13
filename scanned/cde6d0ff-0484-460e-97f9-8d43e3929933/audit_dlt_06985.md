# [M] licenseFee can be greater than BASE

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-09-defiprotocol
Published: 2021-09-21
Source: https://github.com/code-423n4/2021-09-defiprotocol-findings/issues/104
Type: code-finding

## Details
# Handle

itsmeSTYJ


# Vulnerability details

## Impact

Worst case - no functions that contains `handleFees()` can pass because [line 118](https://github.com/code-423n4/2021-09-defiProtocol/blob/main/contracts/contracts/Basket.sol#L118) will always underflow and revert. You only need `feePct` to be bigger than `BASE` for the `handleFees()` function to fail which will result in a lot of gas wasted and potentially bond burnt.

I did not classify this as high risk because a simple fix would simply to reduce the licenseFee via `changeLicenseFee`.

## Recommended Mitigation Steps

Add these require statement to the following functions:

- Basket.changeLicenseFee()
    - `require(newLicenseFee <= BASE, "changeLicenseFee: license fee cannot be greater than 100%");`
- Factory.proposeBasketLicense()
    - `require(licenseFee <= BASE, "proposeBasketLicense: license fee cannot be greater than 100%");`
