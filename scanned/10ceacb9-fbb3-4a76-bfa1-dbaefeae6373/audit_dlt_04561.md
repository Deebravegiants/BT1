# [M] User funds might be at risk by malicious handlers.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-buffer
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-buffer-judging/issues/146
Type: sherlock-finding

## Details
hansfriese

medium

# User funds might be at risk by malicious handlers.

## Summary
User funds might be at risk by malicious handlers.

## Vulnerability Detail
Handlers can transfer funds between any users using `transferFrom()`.

```solidity
    function transferFrom(
        address _sender,
        address _recipient,
        uint256 _amount
    ) public virtual override returns (bool) {
        if (isHandler[msg.sender]) {
            _transfer(_sender, _recipient, _amount);
            return true;
        }

        uint256 currentAllowance = allowance(_sender, msg.sender);
        require(
            currentAllowance >= _amount,
            "Pool: transfer amount exceeds allowance"
        );
        unchecked {
            _approve(_sender, msg.sender, currentAllowance - _amount);
        }
        _transfer(_sender, _recipient, _amount);
        return true;
    }
```

So if a user has positive balances and a malicious handler can transfer his balance to any non-handler account(controlled by him) right after the unlock time.


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-buffer-judging/issues/146_
