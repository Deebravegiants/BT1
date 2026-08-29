# [M] DnGmxJuniorVault.sol#L314 : reset the  `state.protocolEsGmx` to zero, before unstake

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-rage-trade
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-10-rage-trade-judging/issues/75
Type: sherlock-finding

## Details
ak1

medium

# DnGmxJuniorVault.sol#L314 : reset the  `state.protocolEsGmx` to zero, before unstake

## Summary

At [DnGmxJuniorVault.sol#L314](https://github.com/sherlock-audit/2022-10-rage-trade/blob/main/dn-gmx-vaults/contracts/vaults/DnGmxJuniorVault.sol#L314-L321), `unstakeAndVestEsGmx` is called by owner to unstake the `state.protocolEsGmx`. 
Here, it is done such that first deposit is done and then state.protocolEsGmx is set zero.

I think, the way this code is written by thinking that admin is the caller. but imo, it is best practice to reset the value before deposit.
Even if malicious temporary admin wants to disrupt the protocol, then can not do like that.

## Vulnerability Detail

https://github.com/sherlock-audit/2022-10-rage-trade/blob/main/dn-gmx-vaults/contracts/vaults/DnGmxJuniorVault.sol#L314-L321

In above line of codes, unstakeAndVestEsGmx is called to unstake and deposit the `state.protocolEsGmx` 
The `state.protocolEsGmx` is set to zero after the deposit call.
it is possible for a malicious temporary admin to re-enter and cause disruption to the protocol.

But, I see the withdraw has thick safety check. Since it is called externally, this was done. First state.protocolFee taken in a new variable and then set to zero before calling the transfer.

https://github.com/sherlock-audit/2022-10-rage-trade/blob/main/dn-gmx-vaults/contracts/vaults/DnGmxJuniorVault.sol#L306-L311

## Impact

it is possible for a malicious temporary admin to re-enter and cause disruption to the protocol by calling this function again and again.

## Code Snippet

https://github.com/sherlock-audit/2022-10-rage-trade/blob/main/dn-gmx-vaults/contracts/vaults/DnGmxJuniorVault.sol#L314-L321

## Tool used

Manual Review


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-rage-trade-judging/issues/75_
