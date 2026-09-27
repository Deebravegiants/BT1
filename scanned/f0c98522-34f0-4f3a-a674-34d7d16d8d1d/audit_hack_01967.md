# [H] 6.14 Possibility to Exit Positions of Any Address

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security High Version 1 Code Corrected

In ERC20RootVault.withdraw, LP tokens are burned in a call to _burn from the address that is
specified in the to parameter. Neither _burn nor any other statement in withdraw performs access
control checks to verify if the msg.sender is allowed to burn the tokens of the given address. Thus, any
user can burn LP tokens of a given address and transfer the underlying tokens to that address.

Finally, an incorrect event is emitted with msg.sender.

Code corrected:

The issues have been resolved in the updated code Version 2. The function withdraw now burns only
the LP tokens of the msg.sender, while transfers the underlying tokens to the address to specified by
the caller.
