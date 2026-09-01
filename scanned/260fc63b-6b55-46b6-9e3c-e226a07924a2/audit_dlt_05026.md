# [M] Front-runnable DnGmxSeniorVault.sol#updateBorrowCap

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-rage-trade
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-10-rage-trade-judging/issues/35
Type: sherlock-finding

## Details
ctf_sec

medium

# Front-runnable DnGmxSeniorVault.sol#updateBorrowCap

## Summary

The borrower can front run the updateBorrowCap and borrow more than intended.

## Vulnerability Detail

The function updateBorrowCap is vulnerable to front-running.

```solidity
  function updateBorrowCap(address borrowerAddress, uint256 cap) external onlyOwner {
      if (borrowerAddress != address(dnGmxJuniorVault) && borrowerAddress != address(leveragePool))
          revert InvalidBorrowerAddress();

      if (IBorrower(borrowerAddress).getUsdcBorrowed() >= cap) revert InvalidCapUpdate();

      borrowCaps[borrowerAddress] = cap;
      // give allowance to borrower to pull whenever required
      aUsdc.approve(borrowerAddress, cap);

      emit BorrowCapUpdated(borrowerAddress, cap);
  }
```

the borrower can use borrow to front-run the updateBorrowCap.

```solidity
  function borrow(uint256 amount) external onlyBorrower {
      // revert on invalid borrow amount
      if (amount == 0 || amount > availableBorrow(msg.sender)) revert InvalidBorrowAmount();

      // lazily harvest fees (harvest would return early if not enough rewards accrued)
      dnGmxJuniorVault.harvestFees();
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-rage-trade-judging/issues/35_
