# [H] Adversary can siphon funds from JuniorVault by sandwiching their own deposits and withdraws

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-rage-trade
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-10-rage-trade-judging/issues/65
Type: sherlock-finding

## Details
0x52

high

# Adversary can siphon funds from JuniorVault by sandwiching their own deposits and withdraws

## Summary

Each time a user enters the JuniorVault a hedge is automatically opened against their newly added collateral. This causes WBTC/WETH to be borrowed on aave and sold on UNI V3. This trade allows a certain level of slippage to occur, which the depositor can MEV by sandwiching the deposit. The slippage loss from this trade is socialized across the entire vault, meaning that the attacker can profit from this MEV. On withdraw the a portion of the hedge is automatically closed, which can again be sandwiched to extract value. The adversary will have to pay a withdrawal fee but the current withdrawal fee doesn't make the attack unprofitable.

## Vulnerability Detail

    function beforeWithdraw(
        uint256 assets,
        uint256,
        address
    ) internal override {
        (uint256 currentBtc, uint256 currentEth) = state.getCurrentBorrows();

        //rebalance of hedge based on assets after withdraw (before withdraw assets - withdrawn assets)
        state.rebalanceHedge(currentBtc, currentEth, totalAssets() - assets, false);
    }

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

During withdraws and deposits, the hedge is rebalanced to hedge the new amount of assets in the vault. Currently the vault tries to hedge 20% WBTC and 30% WETH, which means that the vault borrows a total of 50% of the value of the deposit/withdraw. The 50% borrow is traded on UNI V3. Currently slippage allows for 1%, allowing the depositor to sandwich this value which is equivalent to 0.5%. The number of shares granted to the depositor is determined before the rebalance happens so the losses are socialized across the entire vault. On withdraw the number of assets received by the user is determined before the rebalance happens. Like before the 1% slippage value can be extracted. Since the assets are determined before the rebalance, the user will receive their entire deposit less the withdraw fee, regardless of the value lost during the withdraw. Currently the slippage has been set to 1% (100 BPS) and withdraw fee has been set to 0.5% (50 bps). With those values, it is profitable to attack the vault. 

Example:

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-rage-trade-judging/issues/65_
