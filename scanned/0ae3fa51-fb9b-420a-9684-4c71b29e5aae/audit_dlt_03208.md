# [H] [WP-H30] A malicious/compromised Registry or Factory admin can drain all the funds from the Vault contracts

## Summary
Severity: High
Chain: Smart contract
Component: 2022-01-insure
Published: 2022-01-13
Source: https://github.com/code-423n4/2022-01-insure-findings/issues/272
Type: code-finding

## Details
# Handle

WatchPug


# Vulnerability details

https://github.com/code-423n4/2022-01-insure/blob/19d1a7819fe7ce795e6d4814e7ddf8b8e1323df3/contracts/Vault.sol#L52-L58

```solidity
modifier onlyMarket() {
    require(
        IRegistry(registry).isListed(msg.sender),
        "ERROR_ONLY_MARKET"
    );
    _;
}
```

https://github.com/code-423n4/2022-01-insure/blob/19d1a7819fe7ce795e6d4814e7ddf8b8e1323df3/contracts/Vault.sol#L201-L206

```solidity
function borrowValue(uint256 _amount, address _to) external onlyMarket override {
    debts[msg.sender] += _amount;
    totalDebt += _amount;

    IERC20(token).safeTransfer(_to, _amount);
}
```

The current design/implementation allows a market address (registered on the `registry`) to call `Vault#borrowValue()` and transfer tokens to an arbitrary address.

## PoC

See the PoC section on [WP-H24].

## Recommendation


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-01-insure-findings/issues/272_
