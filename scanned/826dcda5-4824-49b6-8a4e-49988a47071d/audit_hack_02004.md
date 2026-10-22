# [M] 6.2 Possible to Lock Users' Funds Into veSDT

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 3 Code Corrected

Users that lock their tokens into the voting escrow contract need to approve an allowance to veSDT and
then call deposit_for or deposit_for_from to transfer the tokens. However, if a user approves to
the veSDT an amount that is larger than the intended amount of tokens to be locked, or max uint for
simplicity, the user's tokens are exposed to arbitrary locking. In such cases the function deposit_for
allows anyone to lock more of user's tokens into the contract without their clear consent. This is possible
because the function deposit_for calls the internal function _deposit_for without passing the
msg.sender as a parameter:

```
def deposit_for(_addr: address, _value: uint256):
...
self._deposit_for(_addr, _value, 0, self.locked[_addr], DEPOSIT_FOR_TYPE)
```
The internal function transfers the tokens from _addr if enough allowance exists, while the caller only
pays the gas costs:

```
def _deposit_for(_addr: address, _value: uint256, unlock_time: uint256, locked_balance: LockedBalance, type: int128):
...
if _value != 0:
assert ERC20(self.token).transferFrom(_addr, self, _value)
```
Code corrected

StakeDAO corrected the issue by adding the new parameter _from to _deposit_from and using it
instead of _addr for the ERC20 transfer. Whenever _deposit_from is called, msg.sender is passed
as an argument so that _from is always equal to it. Anyone is still able to call deposit_for or
deposit_for_from for someone else, but it is now the caller's tokens that are deposited.

```
def _deposit_for(_addr: address, _value: uint256, unlock_time: uint256, locked_balance: LockedBalance, type: int128, _from: address):
...
if _value != 0:
assert ERC20(self.token).transferFrom(_from, self, _value)
```
