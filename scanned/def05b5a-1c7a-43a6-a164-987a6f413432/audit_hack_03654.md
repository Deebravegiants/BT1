# [M] Slashing can be frontrun

## Summary
Severity: Medium
Reporter: hickuphh3
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L198-L207
Type: audit-issue

## Details
# Slashing can be frontrun

## Summary
A user that is about to be slashed can frontrun the `slash()` call with a `fullClaimAndExit()` call.

## Vulnerability Detail
A user can actively monitor the mempool for pending `slash()` calls that might slash his TEL stake (and / or claim). He will then be able to frontrun the `slash()` transaction by submitting a `fullClaimAndExit()` call with a much higher gas price to render the slash useless.

## Impact
User is able to escape slashing. 

## Code Snippet
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L198-L207

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L398-L406

## Tool used

Manual Review

## Recommendation
- Impose a reasonably short time waiting period on unstakes / exits
- Submit `slash()` calls via flashbots to avoid mempool detection
