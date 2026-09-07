# [H] Can lock more tokens than in contract

## Summary
Severity: High
Chain: Smart contract
Component: 2021-05-nftx
Published: 2021-05-19
Source: https://github.com/code-423n4/2021-05-nftx-findings/issues/121
Type: code-finding

## Details
# Handle

cmichel


# Vulnerability details


## Vulnerability Details

The `Visor.timeLockERC20` allows locking any amount of tokens exceeding the contract's token balance.

## Impact

The recipient might think that they'll receive the tokens after expiry but it could be that the contract is already out of tokens by then.

## Recommended Mitigation Steps

Make sure that the contract has enough tokens to cover all locks at all times.
