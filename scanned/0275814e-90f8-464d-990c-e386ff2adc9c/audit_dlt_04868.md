# [H] `Factory.sol` lacks methods to revoke signatures

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-nftport
Published: 2022-10-31
Source: https://github.com/sherlock-audit/2022-10-nftport-judging/issues/84
Type: sherlock-finding

## Details
GimelSec

high

# `Factory.sol` lacks methods to revoke signatures

## Summary

Users/Attackers can abuse signatures and the protocol has no way to revoke these signatures.

## Vulnerability Detail

Factory has two methods to call `deploy()` and `call()` functions: `paidOnly` for developers (charging fees), and `signedOnly` for API wallets (doesn't require any fees).
But the protocol doesn't have any methods to revoke signatures under cases where signature abuse happens.

For example, assume that an API wallet `wallet1` has a signature `sign1` with message `abi.encodePacked(wallet1, templateName, initdata)`, the API wallet can call `deploy()` without any fees by using `sign1`.
If the `wallet1` is ever compromised by an attacker, or the controller of `wallet1` decides to go goblin mode and starts abusing the privilege, `Factory` has no means to revoke signature `sign1` and the attacker can always abuse `sign1` without paying any fees.

Another scenario is that if the protocol whitelists some developers, and gives them signatures for calling `deploy()` and `call()` functions without any fees. But this operation causes the protocol to be unable to charge fees from these developers from now on because there's no way to take signatures back.

In general, handing out privilege permanently without considering backup plans for when the privilege should no longer be granted is a bad idea.

## Impact

Developers/Attackers can abuse signatures and the protocol has no ability to revoke these signatures.

## Code Snippet

https://github.com/sherlock-audit/2022-10-nftport/blob/main/evm-minting-master/contracts/Factory.sol#L537

## Tool used

Manual Review

## Recommendation

One solution is to adopt `counter` in signatures:


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-nftport-judging/issues/84_
