# [H] `Ownership` can be claimed by Anyone and  would cause loss of funds to the protocol.

## Summary
Severity: High
Reporter: shealtielanz
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L75C1-L76C28
Type: audit-issue

## Details
# `Ownership` can be claimed by Anyone and  would cause loss of funds to the protocol.

## Summary
In most of the contracts of `Unstoppable`, the `_init_` function is used to set the owner in the contract, however, that function can be called by anyone since it is external and has no access control, where it could also be called multiple times, an attacker can simply call that function and claim the fees to be sent to the supposed owner.
## Vulnerability Detail
A Breakdown Instance of this issue.
In  `TrailingStopDex.vy` the `__init__()` function --->  [Click here](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L75C1-L76C28)
```vyper
@external
def __init__():
    self.owner = msg.sender
```
This function doesn't have any protection and could be called by anyone to set the caller as the owner.
Now look  `withdraw_fees` function  ------>  [Click here](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L216C1-L220C47)

```vyper
@external
def withdraw_fees(_token: address):
    amount: uint256 = ERC20(_token).balanceOf(self)
    assert amount > 0, "zero balance"

    ERC20(_token).transfer(self.owner, amount)
```
Here you can see that if the contract has accumulated fees, a malicious actor can simply claim ownership and call the `withdraw_fees` function to send to himself all the fees gained by the contract. 
This is only `one` Impact of what an attacker can do if he claims ownership of the contract.

This issue is seen in all the `contracts` of the protocol. 
- `TrailingStopDex.vy`
- `LimitOrders.vy`
- `Dca.vy`
- `Vault.vy`
- `SwapRouter.vy`
- `MarginDex.vy`
## Impact
This is catastrophic to the protocol where an attacker can claim ownership of the protocol, claim fees gain by the protocol, have access to set functions that is to be controlled by only the owner.
## Code Snippet
- `TrailingStopDex.vy` ~  [Click Here](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L74C1-L76C28)
- `LimitOrders.vy` ~  [Click Here](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L68C1-L70C28)
- `Dca.vy`  ~   [Click Here](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L85C1-L87C27)
- `Vault.vy`  ~  [Click Here](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L145C1-L148C44)
- `SwapRouter.vy` ~  [Click Here](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L55C1-L57C28)
- `MarginDex.vy`  ~   [Click Here](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L109C1-L111C28)
## Tool used 

Manual Review

## Recommendation
properly initialize the owner, and put access controls on the __init__ function to protect it from malicious actors.
