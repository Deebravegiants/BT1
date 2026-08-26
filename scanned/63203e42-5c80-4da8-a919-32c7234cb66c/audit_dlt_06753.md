# [M] PirexGmx.initiateMigration can be blocked

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-redactedcartel
Published: 2022-11-23
Source: https://github.com/code-423n4/2022-11-redactedcartel-findings/issues/61
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-11-redactedcartel/blob/main/src/PirexGmx.sol#L921-L935


# Vulnerability details

## Impact
PirexGmx.initiateMigration can be blocked so contract will not be able to migrate his funds to another contract using gmx.

## Proof of Concept
PirexGmx was designed with the thought that the current contract can be changed with another during migration.
PirexGmx.initiateMigration is the first point in this long process. 
https://github.com/code-423n4/2022-11-redactedcartel/blob/main/src/PirexGmx.sol#L921-L935
```solidity
    function initiateMigration(address newContract)
        external
        whenPaused
        onlyOwner
    {
        if (newContract == address(0)) revert ZeroAddress();


        // Notify the reward router that the current/old contract is going to perform
        // full account transfer to the specified new contract
        gmxRewardRouterV2.signalTransfer(newContract);


        migratedTo = newContract;


        emit InitiateMigration(newContract);
    }
```
As you can see `gmxRewardRouterV2.signalTransfer(newContract);` is called to start migration.
This is the code of signalTransfer function
https://arbiscan.io/address/0xA906F338CB21815cBc4Bc87ace9e68c87eF8d8F1#code#F1#L282
```solidity
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-11-redactedcartel-findings/issues/61_
