# [H] 5.2.4 Unsetgovernorallows to steal both yield and gas refund

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk

**Context:** Blast.sol#L

**Description:** CrossDomainMessengerpredeploy does not have itsgovernorconfigured inBlast.sol. This means
that if an attacker sends a message to L2 like shown below, then it would become thegovernorof theCrossDo-
mainMessengercontract:

```
//`relayMessage`called with:
```
```
_target = Blast contract
selector = configure
_yieldMode = Automatic
Gasmode = CLAIMABLE
governor = Attacker
```
This allows them to claim:

1. Yield from the collected ETH inL2CrossDomainMessenger, if therelayMessage(temporarily) failed.
2. Gas for theL2CrossDomainMessenger.

Note: This issue affects any contract on L2 that allows arbitrary calls.

**Recommendation:** AddBlastcontract to_isUnsafeTargetor initialize the predeploy with itself as the governor.
Also, for all L2 contracts allowing arbitrary calls, consider setting some governor to prevent an attacker from taking


# DRAFT

control.
