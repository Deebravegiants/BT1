# [M] QA Report

## Summary
Severity: Medium
Source: https://github.com/code-423n4/2022-02-hubble/blob/main/contracts/ClearingHouse.sol#L341
Type: audit-issue

## Details
LOW : 
1. 
Title : Missing limit on how many AMMs can be added

Impact : 
The governance can add an amm, by calling whitelistAmm function, however there is no limit on how many amm that the contract can be held, if the governance keep adding amm, then the clearing house will brick with out of gas, since all other user is interacting with the clearing house and the main functionality of this contract is updatePoition and this function is being called by removeLiquidity, addLiquidity, openPosition, closePosition function

POC : 
https://github.com/code-423n4/2022-02-hubble/blob/main/contracts/ClearingHouse.sol#L341

2. 
Title : Missing check on duplicate amm

Impact : 
There is missing check on axisting amm, and amm that will going to be added from whitelistAmm function, since there is no check whether the same amm is already being added or not, a multiple amm might be added without error.

POC : 
https://github.com/code-423n4/2022-02-hubble/blob/main/contracts/ClearingHouse.sol#L341

3. 
Title : Grieve in processWtihdrawals

Impact : an attacker could grieve other user by burning many small amount VUSD, to inflate the withdrawals length until 99, and if the victim want to burn their VUSD to USDC, the victim will be placed in the 100, and when the victim want to take the USDC, by calling processWithdrawal, the victim will pay extra fee, that's because the victim must process the withdrawal that the attacker make 99 times, before the victim accept their USDC.

POC : 
1. An attacker mint 100 wei VUSD, with USDC
2. Burn 1 wei VUSD
3. Repeat step 2 99 times
4. The victim use burn function to get USDC back, however the victim must pay extra gas, just to send 1 wei that was belong to the attacker.

https://github.com/code-423n4/2022-02-hubble/blob/main/contracts/VUSD.sol#L53
