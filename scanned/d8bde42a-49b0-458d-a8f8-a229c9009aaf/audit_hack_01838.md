# [H] Holders can burn locked funds

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

Skale token is a modified ERC-777 that allows locking some part of the balance. Locking is checked during every transfer:


**code/contracts/ERC777/LockableERC777.sol:L433-L441**
```solidity
// Property of the company SKALE Labs inc.---------------------------------
        uint locked = _getLockedOf(from);
        if (locked > 0) {
            require(_balances[from] >= locked + amount, "Token should be unlocked for transferring");
        }
//-------------------------------------------------------------------------
        _balances[from] = _balances[from].sub(amount);
        _balances[to] = _balances[to].add(amount);

```

But it's not checked during `burn` function and it's possible to "burn" locked tokens. Tokens will be burned, but `locked` amount will remain the same. That will result in having more `locked` tokens than the balance which may have very unpredictable behaviour. 

#### Recommendation

Allow burning only unlocked tokens.
