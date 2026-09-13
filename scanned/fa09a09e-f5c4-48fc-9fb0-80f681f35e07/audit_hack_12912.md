# [M] Admin role inflexibility: lack of transfer mechanism in SwapRouter.vy

## Summary
Severity: Medium
Reporter: 0x4non
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L56-L57
Type: audit-issue

## Details
# Admin role inflexibility: lack of transfer mechanism in SwapRouter.vy

## Summary

The SwapRouter contract in the given codebase assigns an `admin` role upon initialization, with no subsequent provision to change this role. This could become a major issue if the role of `admin` needs to be transferred, given the critical functionality only accessible to the admin (like `add_direct_route` and `add_path`).

## Vulnerability Detail

The `__init__` function of the SwapRouter contract assigns the `admin` role to the `msg.sender` upon contract deployment. But, no subsequent function is provided to change this admin. This poses a problem because the admin role is critical for certain functions, such as `add_direct_route` and `add_path`, which are necessary for maintaining the flexibility and functionality of the contract.


## Impact

This issue makes it impossible to change the admin role once the contract has been deployed. If the initial admin leaves the project, loses access to their address, or for any reason can no longer function as the admin, this could result in the inability to properly manage the contract.

## Code Snippet

[SwapRouter.vy#L56-L57](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L56-L57)
```vyper
@nonpayable
@external
def __init__():
    self.admin = msg.sender
```
There is no way of changing `admin`, and only admin can access to:
- [add_direct_route](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L124-L125)
- [add_path](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L131-L132)

## Tool used

Manual Review

## Recommendation

It is recommended to include functionality to allow the admin role to be transferred. This could involve a suggest_admin function that nominates a new admin, and an accept_admin function that allows the new admin to accept their nomination. Such functionality can be found in [/MarginDex.vy#L795-L825](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L795-L825)
