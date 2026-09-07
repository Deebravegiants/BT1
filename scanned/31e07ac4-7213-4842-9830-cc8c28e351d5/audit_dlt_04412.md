# [H] An attacker can open an account whose owner has been closed

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-sentiment
Published: 2022-11-04
Source: https://github.com/sherlock-audit/2022-11-sentiment-judging/issues/11
Type: sherlock-finding

## Details
8olidity

high

# An attacker can open an account whose owner has been closed

## Summary
An attacker can open an account whose owner has been closed
## Vulnerability Detail
The `owner` and `msg.sender` are not verified by `openAccount()`. Any user can activate the user whose owner is disabled

```solidity
    function openAccount(address owner) external nonReentrant whenNotPaused {
        if (owner == address(0)) revert Errors.ZeroAddress();
        address account;
        uint length = inactiveAccountsOf[owner].length;
        if (length == 0) { // owner对应没有account
            account = accountFactory.create(address(this));
            IAccount(account).init(address(this));
            registry.addAccount(account, owner);
        } else {                                                  
            account = inactiveAccountsOf[owner][length - 1];
            inactiveAccountsOf[owner].pop();
            registry.updateAccount(account, owner);
        }
        IAccount(account).activate();
        emit AccountAssigned(account, owner);
    }
```

#### poc
`address(2)` activates the `account1` account that the user has already closed, and `user` calls `openaccount() `again to get a new account address instead of the previous one.

```solidity
    function testTwoaccout() public {
        address account1 = openAccount(user);
        cheats.roll(block.number + 1);
        cheats.prank(user);
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-sentiment-judging/issues/11_
