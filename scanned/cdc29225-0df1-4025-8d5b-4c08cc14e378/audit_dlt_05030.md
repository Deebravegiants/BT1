# [M] DnGmxJuniorVault.maxDeposit and DnGmxJuniorVault.afterDeposit calculate maximum assets that are allowed to deposit in different ways

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-rage-trade
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-10-rage-trade-judging/issues/23
Type: sherlock-finding

## Details
rvierdiiev

medium

# DnGmxJuniorVault.maxDeposit and DnGmxJuniorVault.afterDeposit calculate maximum assets that are allowed to deposit in different ways

## Summary
DnGmxJuniorVault.maxDeposit and DnGmxJuniorVault.afterDeposit calculate maximum assets that are allowed to deposit in different ways.
## Vulnerability Detail
This is how DnGmxJuniorVault.maxDeposit function calculates max amount of assets that are allowed to deposit.
https://github.com/sherlock-audit/2022-10-rage-trade/blob/main/dn-gmx-vaults/contracts/vaults/DnGmxJuniorVault.sol#L531-L533
```solidity
    function maxDeposit(address) public view override(IERC4626, ERC4626Upgradeable) returns (uint256) {
        return state.depositCap - state.totalAssets(true);
    }
```

And this is how DnGmxJuniorVault.afterDeposit function calculates max amount of assets that are allowed to deposit.
https://github.com/sherlock-audit/2022-10-rage-trade/blob/main/dn-gmx-vaults/contracts/vaults/DnGmxJuniorVault.sol#L719-L729
```solidity
    function afterDeposit(
        uint256,
        uint256,
        address
    ) internal override {
        if (totalAssets() > state.depositCap) revert DepositCapExceeded();
        (uint256 currentBtc, uint256 currentEth) = state.getCurrentBorrows();


        //rebalance of hedge based on assets after deposit (after deposit assets)
        state.rebalanceHedge(currentBtc, currentEth, totalAssets(), false);
    }
```

As you can see in one case it uses `totalAssets()` function to get all assets.
```solidity
    function totalAssets() public view override(IERC4626, ERC4626Upgradeable) returns (uint256) {
        return state.totalAssets();
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-rage-trade-judging/issues/23_
