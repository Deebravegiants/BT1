# [?] docs: fix reentrancy vulnerability in micropayment close() example (#16497)

## Summary
Severity: Unknown
Chain: Solidity
Component: ethereum/solidity
Published: 2026-03-10
Source: https://github.com/argotorg/solidity/commit/de054d1d44e4c530e0c89feb6eb7bb369648fb61
Type: security-commit

## Details
docs: fix reentrancy vulnerability in micropayment close() example (#16497)

Move freeze() call before external calls to follow
the Checks-Effects-Interactions pattern and prevent
reentrancy attacks in the SimplePaymentChannel contract.
