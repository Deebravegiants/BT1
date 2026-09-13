# [M] 6.2 Refund Recipient Is Not Aliased

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 5 Code Corrected

On ZkSync the contract addresses are aliased using the AddressAliasHelper.applyL1ToL2Alias
function, to distinguish between L1 and L2 initiated transactions. However, the refund recipient in the
Mailbox.requestL2Transaction call in the L1DAITokenBridge contract doesn't alias the
msg.sender address, even if it is a contract address.

Code corrected:

Refund recipient address is aliased if the msg.sender is a contract.
