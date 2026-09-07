# [H] Permissionless `settleVault` Function Within `CrossCurrencyfCashVault` Vault Can Be Exploited To Steal Profit

## Summary
Severity: High
Chain: Smart contract
Component: 2022-09-notional
Published: 2022-10-13
Source: https://github.com/sherlock-audit/2022-09-notional-judging/issues/81
Type: sherlock-finding

## Details
xiaoming90

high

# Permissionless `settleVault` Function Within `CrossCurrencyfCashVault` Vault Can Be Exploited To Steal Profit

## Summary

The permissionless `settleVault` function within `CrossCurrencyfCashVault` vault can be exploited to steal the profit of the vaults.

## Vulnerability Detail

The `CrossCurrencyfCashVault.settleVault` function is permissionless and can be called by anyone.

https://github.com/sherlock-audit/2022-09-notional/blob/main/leveraged-vaults/contracts/vaults/CrossCurrencyfCashVault.sol#L121

```solidity
File: CrossCurrencyfCashVault.sol
121:     function settleVault(uint256 maturity, uint256 strategyTokens, bytes calldata settlementTrade) external {
122:         require(maturity <= block.timestamp, "Cannot Settle");
123:         VaultState memory vaultState = NOTIONAL.getVaultState(address(this), maturity);
124:         require(vaultState.isSettled == false);
125:         require(vaultState.totalStrategyTokens >= strategyTokens);
			 ..SNIP..
```

Following is an example of a `CrossCurrencyfCashVault.settleVault` call taken from the test scripts for reference.

https://github.com/sherlock-audit/2022-09-notional/blob/main/leveraged-vaults/tests/test_cross_currency.py#L265

```solidity
File: test_cross_currency.py
265:     txn = usdcDaiVault.settleVault(
266:         maturity,
267:         vaultState['totalStrategyTokens'],
268:         encode_redeem_params(
269:             minPurchaseAmount=Wei(129_500e6),
270:             maxBorrowRate=0,
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-09-notional-judging/issues/81_
