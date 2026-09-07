# [H] Incorrect usage of `_pow` in `_computeSingleOutGivenPoolIn` of `IndexPool`

## Summary
Severity: High
Chain: Smart contract
Component: 2021-09-sushitrident
Published: 2021-09-29
Source: https://github.com/code-423n4/2021-09-sushitrident-findings/issues/165
Type: code-finding

## Details
# Handle

broccoli


# Vulnerability details

## Impact

The `_computeSingleOutGivenPoolIn` function of `IndexPool` uses the `_pow` function to calculate `tokenOutRatio` with the exponent in `WAD` (i.e., in 18 decimals of precision). However, the `_pow` function assumes that the given exponent `n` is not in `WAD`. (for example, `_pow(5, BASE)` returns `5 ** (10 ** 18)` instead of `5 ** 1`). The misuse of the `_pow` function could causes an integer overflow in the `_computeSingleOutGivenPoolIn` function and thus prevent any function from calling it.

## Proof of Concept

Referenced code:
[IndexPool.sol#L279](https://github.com/sushiswap/trident/blob/9130b10efaf9c653d74dc7a65bde788ec4b354b5/contracts/pool/IndexPool.sol#L279)


## Recommended Mitigation Steps

Change the `_pow` function to the `_compute` function, which supports exponents in `WAD`.
