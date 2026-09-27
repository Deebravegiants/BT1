# [M] updating the state 

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-03-paladin
Published: 2022-04-02
Source: https://github.com/code-423n4/2022-03-paladin-findings/issues/27
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-03-paladin/blob/9c26ec8556298fb1dc3cf71f471aadad3a5c74a0/contracts/HolyPaladinToken.sol#L1338


# Vulnerability details

## Impact
In the Emergency withdraw function  userCurrentBonusRatio and  durationRatio aren't update which will user clime funds with the wrong ratio 
## Proof of Concept
https://github.com/code-423n4/2022-03-paladin/blob/9c26ec8556298fb1dc3cf71f471aadad3a5c74a0/contracts/HolyPaladinToken.sol#L1338

## Tools Used
Manual
## Recommended Mitigation Steps
set  these variables to zero in the EmergencyWithdraw function
