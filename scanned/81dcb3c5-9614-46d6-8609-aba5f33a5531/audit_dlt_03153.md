# [M] Deposits don't work with fee-on transfer tokens

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-06-realitycards
Published: 2021-06-16
Source: https://github.com/code-423n4/2021-06-realitycards-findings/issues/152
Type: code-finding

## Details
# Handle

cmichel


# Vulnerability details

## Vulnerability Details

There are ERC20 tokens that may make certain customizations to their ERC20 contracts.
One type of these tokens is deflationary tokens that charge a certain fee for every `transfer()` or `transferFrom()`.


## Impact

The `deposit()` function will introduce unexpected balance inconsistencies when comparing internal asset records with external ERC20 token contracts.

## Recommended Mitigation Steps

 One possible mitigation is to measure the asset change right before and after the asset-transferring routines
