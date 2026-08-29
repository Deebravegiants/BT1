# [H] Attacker can forge `CardTopup` events

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-mover
Published: 2022-10-28
Source: https://github.com/sherlock-audit/2022-10-mover-judging/issues/114
Type: sherlock-finding

## Details
WATCHPUG

high

# Attacker can forge `CardTopup` events

## Summary

`CardTopup` events can be forged with fake topup transactions by using 1inch as the bridge.

## Vulnerability Detail

Per to deploy script, the same `trustedregistry` will be shared among `exchangeproxy` and `topupproxy`.

Therefore, the 2 whitelisted swap aggregator contracts will also be allowed to be called on `topupproxy`:

- 0x Proxy
- 1inch Proxy

Also, the design of `1inch`'s `AggregationRouterV4` can be used to pull funds from the `topupproxy` and execute arbitrary external call:

https://polygonscan.com/address/0x1111111254fb6c44bAC0beD2854e76F90643097d#code

See L2309-2321.

---

Therefore, the attacker can craft a transaction with 1inch as the bridge's `targetAddress` which can be used to claw back the funds.

## Impact

While the attacker actual does not pay for the topup, there will be a pretty authentic `CardTopup` event, which according to the comment:

> this event is important for the backend to track topup activity, esp. store receiverHash

> that could provide ability to topup topup tag associated with arbitrary card/address

## Code Snippet

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-mover-judging/issues/114_
