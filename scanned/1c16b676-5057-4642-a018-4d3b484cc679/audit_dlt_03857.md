# [M] FRAX admin can adjust fee rate to harm Napier and its users

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-01-napier
Published: 2024-02-27
Source: https://github.com/sherlock-audit/2024-01-napier-judging/issues/108
Type: sherlock-finding

## Details
xiaoming90

medium

# FRAX admin can adjust fee rate to harm Napier and its users

## Summary

FRAX admin can adjust fee rates to harm Napier and its users, preventing Napier users from withdrawing.

## Vulnerability Detail

Per the contest page, the admins of the protocols that Napier integrates with are considered "RESTRICTED". This means that any issue related to FRAX's admin action that could negatively affect Napier protocol/users will be considered valid in this audit contest.

> Q: Are the admins of the protocols your contracts integrate with (if any) TRUSTED or RESTRICTED?
> RESTRICTED

Following is one of the ways that FRAX admin can harm Napier and its users.

FRAX admin can set the fee to 100%.

https://etherscan.io/address/0x82bA8da44Cd5261762e629dd5c605b17715727bd#code#L3413

```solidity
File: FraxEtherRedemptionQueue.sol
217:     /// @notice Sets the fee for redeeming
218:     /// @param _newFee New redemption fee given in percentage terms, using 1e6 precision
219:     function setRedemptionFee(uint64 _newFee) external {
220:         _requireSenderIsTimelock();
221:         if (_newFee > FEE_PRECISION) revert ExceedsMaxRedemptionFee(_newFee, FEE_PRECISION);
222: 
223:         emit SetRedemptionFee({ oldRedemptionFee: redemptionQueueState.redemptionFee, newRedemptionFee: _newFee });
224: 
225:         redemptionQueueState.redemptionFee = _newFee;
226:     }
```

When the adaptor attempts to redeem the staked ETH from FRAX via the `enterRedemptionQueue` function, the 100% fee will consume the entire amount of the staked fee, leaving nothing for Napier's adaptor.

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2024-01-napier-judging/issues/108_
