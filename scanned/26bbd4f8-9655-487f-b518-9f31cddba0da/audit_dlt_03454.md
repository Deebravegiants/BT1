# [M] `NoYield.sol` Tokens with fee on transfer are not supported

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-12-sublime
Published: 2021-12-15
Source: https://github.com/code-423n4/2021-12-sublime-findings/issues/142
Type: code-finding

## Details
# Handle

WatchPug


# Vulnerability details

There are ERC20 tokens that charge fee for every `transfer()` or `transferFrom()`.

In the current implementation, `NoYield.sol#lockTokens()` assumes that the received amount is the same as the transfer amount, and uses it to calculate `sharesReceived` amounts.

As a result, in `unlockTokens()`, later users may not be able to successfully withdraw their tokens, as it may revert at L141 for insufficient balance.

https://github.com/code-423n4/2021-12-sublime/blob/9df1b7c4247f8631647c7627a8da9bdc16db8b11/contracts/yield/NoYield.sol#L93-L106

```solidity
    function lockTokens(
        address user,
        address asset,
        uint256 amount
    ) external payable override onlySavingsAccount nonReentrant returns (uint256 sharesReceived) {
        require(amount != 0, 'Invest: amount');
        if (asset != address(0)) {
            IERC20(asset).safeTransferFrom(user, address(this), amount);
        } else {
            require(msg.value == amount, 'Invest: ETH amount');
        }
        sharesReceived = amount;
        emit LockedTokens(user, asset, sharesReceived);
    }
```

https://github.com/code-423n4/2021-12-sublime/blob/9df1b7c4247f8631647c7627a8da9bdc16db8b11/contracts/yield/NoYield.sol#L134-L144

```solidity
    function _unlockTokens(address asset, uint256 amount) internal returns (uint256 received) {
        require(amount != 0, 'Invest: amount');
        received = amount;
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2021-12-sublime-findings/issues/142_
