# [M] OCL_ZVE.sol::forwardYield relies on manip-

## Summary
Severity: Medium
Contest weight: 0.5833
Dataset id: 22696
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
OCL_ZVE.sol::forwardYield is used to forward yield in excess of the basis but it relies on Uniswap V2 pools that can be manipulable by an attacker to set basis to a very small amount and steal funds. fetchBasis is a function which returns the amount of pairAsset (USDC) which is claimable by burning the balance of LP tokens of OCL_ZVE. fetchBasis is called first in forwardYield in order to determine the yield to distribute:
```solidity
(uint256 amount, uint256 lp) = fetchBasis();
if (amount > basis) { _forwardYield(amount, lp); }
(basis,) = fetchBasis();
```
If the returned amount is <= basis (negative yield) no yield is forwarded and basis is updated to the low amount value. By manipulating the Uniswap V2 pool with a flashloan, an attacker can get the uint256 amount value returned by OCL_ZVE.sol::fetchBasis to be very small and set basis to this very small value:
```solidity
if (amount > basis) { _forwardYield(amount, lp); }
(basis,) = fetchBasis();
```
The next call (30 days later) to OCL_ZVE.sol::forwardYield will forward much more yield (in excess of basis) than it should, leading to a loss of funds for the protocol. Scenario 1. Attacker buys a very large amount of USDC in the Uniswap V2 pool ZVE/pairAsset (can use a flash-loan if needed) 2. Attacker calls OCL_ZVE.sol::forwardYield • OCL_ZVE.sol::fetchBasis returns an incorrect and very small value for amount: • No yield is forwarded since amount < basis • OCL_ZVE.sol::forwardYield sets basis to amount 3. Attacker backruns the calls to OCL_ZVE.sol::forwardYield with the sell of his large buy in the Uniswap V2 pool 4. 30 days later, Attacker calls OCL_ZVE.sol::forwardYield and steal funds in excess of basis Loss of funds for the protocol.

## Recommendation
Consider reverting during a call to forwardYield if amount <= basis
