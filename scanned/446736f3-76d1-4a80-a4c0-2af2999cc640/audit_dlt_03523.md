# [H] Token balances can be updated in pools without first sending tokens because of missing/permissive access control in Pools.sol

## Summary
Severity: High
Chain: Smart contract
Component: 2021-04-vader
Published: 2021-04-27
Source: https://github.com/code-423n4/2021-04-vader-findings/issues/123
Type: code-finding

## Details
# Handle

0xRajeev


# Vulnerability details

## Impact

The sync() function in Pools.sol is expected to be called only from the Router's payInterest/_handlePoolReward functions, where those Router functions perform the necessary checks/accounting and enforce transfer of tokens to pools before calling this sync() function. 

However, given the external visibility of Pools’ sync() function, this function can be called directly by an attacker to manipulate protocol accounting by updating token balances bypassing Router’s checks/accounting and actual transfer of tokens to pools. This will break protocol invariants for accounting and functioning. Protocol will break and funds may be lost.

## Proof of Concept

https://github.com/code-423n4/2021-04-vader/blob/3041f20c920821b89d01f652867d5207d18c8703/vader-protocol/contracts/Pools.sol#L121-L132

https://github.com/code-423n4/2021-04-vader/blob/3041f20c920821b89d01f652867d5207d18c8703/vader-protocol/contracts/Router.sol#L189

https://github.com/code-423n4/2021-04-vader/blob/3041f20c920821b89d01f652867d5207d18c8703/vader-protocol/contracts/Router.sol#L367


## Tools Used

Manual Analysis

## Recommended Mitigation Steps

Add access control (e.g. via a modifier onlyRouter) so sync() function of Pools contract can be called only from Router contract whose _handleRewards() and payInterest() functions do checks/accounting and actual transfer of tokens to pools before calling sync() function of Pools contract.
