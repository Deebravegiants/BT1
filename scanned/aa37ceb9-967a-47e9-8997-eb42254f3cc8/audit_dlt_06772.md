# [M] Mitigation Confirmed for M-02

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-05-asymmetry-mitigation
Published: 2023-05-08
Source: https://github.com/code-423n4/2023-05-asymmetry-mitigation-findings/issues/15
Type: code-finding

## Details
Note: Issue has not actually been resolved but for some reason I can't get my issues to submit without "Mitigation confirmed (no new vulnerabilities detected)" checked so I am doing this as a work around

## Severity

Medium

## Lines of code

https://github.com/code-423n4/2023-03-asymmetry/blob/44b5cd94ebedc187a08884a7f685e950e987261c/contracts/SafEth/derivatives/SfrxEth.sol#L61-L65

## Impact

During situation presented in M-02 submission the owner must choose between loss of funds or guaranteed downtime

## Proof of Concept

The root issue of M-02 is still present and simply disabling the derivative isn't a very good solution. This is because when a derivative is disabled all funds inside that derivative are now irretrievable. In the scenario presented by the original submission the owner of the contract would have to wait until the underlying derivative is reverting before they can disable the contract, putting the owner in a catch 22 situation:

1) Remove the derivative early and cause safETH holders to lose funds (since remainder will be inaccessible
2) Users experience guaranteed downtimes on withdrawals/deposits

## Tools Used

Manual Review

## Recommended Mitigation Steps

Implement the original mitigation suggested in M-02
