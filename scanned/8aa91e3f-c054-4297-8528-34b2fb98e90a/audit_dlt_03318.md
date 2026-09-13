# [M] lack of validation for the v and s value in  recover() funciton 

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-08-gravitybridge
Published: 2021-09-08
Source: https://github.com/code-423n4/2021-08-gravitybridge-findings/issues/43
Type: code-finding

## Details
# Handle

JMukesh


# Vulnerability details

## Impact
due to lack of checking of v and s value in recover() it become prone to signature malleability


## Proof of Concept
check out the tryRecover() of ECDSA.sol

https://github.com/OpenZeppelin/openzeppelin-contracts/blob/aefcb3e8aa4ee8da8e2b7022ffe4dcb57fbb0fdf/contracts/utils/cryptography/ECDSA.sol#L147

## Tools Used

manual reveiw

## Recommended Mitigation Steps
add necessary check to make the signature unique
