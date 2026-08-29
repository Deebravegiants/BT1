# [M] yieldDistributorAddress' fees could be stolen by admin

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-mover
Published: 2022-10-28
Source: https://github.com/sherlock-audit/2022-10-mover-judging/issues/34
Type: sherlock-finding

## Details
Miguel

medium

# yieldDistributorAddress' fees could be stolen by admin

## Summary
Admin users have the privilege to change `yieldDistributorAddress` that is correct but It could cause that previous yieldDistributor loose its fees.

## Vulnerability Detail
Assumption:
Previous `yieldDistributor` has a big amount in fees to claim.

Check the following steps
- Original `yieldDistributor` has more 100 ETH (or any big amount) in fees to claim.
- Admin decided to set a new `yieldDistributor`,
- New `yieldDistributor` claims for the fees that belongs to the previous one.

I mean that admin in the unique failure point in the process. So you are only trusting in the admins good intentions but it could be broken due to big amounts of money. It could happen if some private key's admin are stolen even.

The code does not protect (and should from my point of view) to the original `yieldDistributor` which is an interested actor in the process.

## Impact

ExchangeProxy.sol

## Code Snippet

`setYieldDistributor` method:
https://github.com/sherlock-audit/2022-10-mover/blob/main/cardtopup_contract/contracts/ExchangeProxy.sol#L224-L229

`claimFees` method:
https://github.com/sherlock-audit/2022-10-mover/blob/main/cardtopup_contract/contracts/ExchangeProxy.sol#L242-L249
## Tool used

Manual Review

## Recommendation

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-mover-judging/issues/34_
