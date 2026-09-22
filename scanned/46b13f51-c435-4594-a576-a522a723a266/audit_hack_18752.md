# [M] `SolverVault` add fallback function and receive function

## Summary
Severity: Medium
Reporter: Generous Lava Donkey
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# `SolverVault` add fallback function and receive function

## Summary

Adding fallback and a receive  function will allow the contract be able to get sent money to it

## Vulnerability Detail

if money is sent to this contract it will revert

## Impact

if money is sent to this contract it will revert

## Code Snippet

## Tool used

Manual Review

## Recommendation
add fallback function and receive function that are payable
