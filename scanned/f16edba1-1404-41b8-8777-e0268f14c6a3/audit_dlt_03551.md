# [M] Governed.sol: setPendingGov() should use the emergency_governed modifier.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-11-streaming
Published: 2021-12-03
Source: https://github.com/code-423n4/2021-11-streaming-findings/issues/72
Type: code-finding

## Details
# Handle

itsmeSTYJ


# Vulnerability details

## Impact

In the event the governor gets compromised (leaked pk, unauthorised remote access, phishing etc.), you will not be able to recover it with the emergency governor however if the emergency governor gets compromised, you can still resolve the problem w/ the governor.

The scope of damage is limited as the governor is only used for claiming fees and for making arbitrary calls.

## Recommended Mitigation Steps

`Locke.setPendingGov()` should use the `emergency_governed` modifier
