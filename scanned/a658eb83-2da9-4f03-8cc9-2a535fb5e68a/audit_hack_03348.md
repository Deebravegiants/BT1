# [H] Lack of `reentrancy` guard for swap operation

## Summary
Severity: High
Reporter: ak1
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L164-L387
Type: audit-issue

## Details
# Lack of `reentrancy` guard for swap operation

## Summary
The swaps operation are not safeguarded from reentrancy attack.

## Vulnerability Detail
It is well known issue. 
when we look at the `externalSwap`, `mixSwap` or `dodoMutliSwap`, it swaps the amount and send the swapped amount to msg.sender.
The msg.sender either can be a smart contract or EOA.
If it is smart contract then it is issue. The malicious contract can have function for reentrancy case.

## Impact

Re-entrance issue can cause theft of fund.
Major hack and lose of fund happened due to this kind of hack.
Refer the link for consequences of this hack
https://github.com/sherlock-audit/2022-11-sense-judging/issues/40#:~:text=Impact,through%20reentrancy%20attack.)

## Code Snippet
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L164-L387

## Tool used

Manual Review

## Recommendation
When a contract interacts with unknown ERC20 tokens it is better to be safe and consider that transfers can create reentrancy problems.

Use openzeppalin/solmate reentrancy protection guard.

pragma solidity 0.8.13;

    contract ReEntrancyGuard {
    bool internal locked;

    modifier noReentrant() {
        require(!locked, "No re-entrancy");
        locked = true;
        _;
        locked = false;
    }

   }
