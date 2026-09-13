# [M] In  `` GovernorBravoDelegate :: _acceptAdmin() `` ,  the custom error wrongly check if msg.sender is the address(0)

## Summary
Severity: Medium
Reporter: Lucky Heather Worm
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# In  `` GovernorBravoDelegate :: _acceptAdmin() `` ,  the custom error wrongly check if msg.sender is the address(0)

The comment says     `` // Check caller is pendingAdmin and pendingAdmin ≠ address(0) `` but the custom error check if   `` msg.sender == address(0) `` instead of `` pendingAdmin == address(0) ``




This is the correct implementation in your context or you can remove the second check and only do   `` msg.sender != pendingAdmin ``
```
    if (    msg.sender != pendingAdmin   ||   pendingAdmin == address(0)    ) {


        revert GovernorBravo_OnlyPendingAdmin();


    }

```
