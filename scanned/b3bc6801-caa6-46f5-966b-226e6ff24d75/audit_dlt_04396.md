# [H] withdrawInsurance can revert unexpectedly because of the free collateral utilization rate and the funding rate on Perp protocol

## Summary
Severity: High
Chain: Smart contract
Component: 2023-01-uxd
Published: 2023-01-25
Source: https://github.com/sherlock-audit/2023-01-uxd-judging/issues/82
Type: sherlock-finding

## Details
ctf_sec

high

# withdrawInsurance can revert unexpectedly because of the free collateral utilization rate and the funding rate on Perp protocol

## Summary

withdrawInsurance can revert unexpectedly because of the free collateral utilization rate and the funding rate on Perp protocol

## Vulnerability Detail

In the current implementation of perpDepository, we have two functions:

depositInsurane and withdrawInsurance

```solidity
function depositInsurance(uint256 amount, address from)
	external
	nonReentrant
	onlyOwner
{
	if (amount == 0) {
		revert ZeroAmount();
	}
	uint256 allowance = IERC20(insuranceToken()).allowance(
		from,
		address(this)
	);
	if (allowance < amount) {
		revert NotApproved(allowance, amount);
	}

	insuranceDeposited += amount;

	IERC20(insuranceToken()).transferFrom(from, address(this), amount);
	IERC20(insuranceToken()).approve(address(vault), amount);
	vault.deposit(insuranceToken(), amount);
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2023-01-uxd-judging/issues/82_
