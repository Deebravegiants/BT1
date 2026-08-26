# [M] Malicious BLACKLISTER_ROLE can temporarily block burning mechanism blacklisting address(0)

## Summary
Severity: Medium
Chain: Smart contract
Component: Euro-Dollar
Published: 2024-11-06
Source: https://github.com/hats-finance/Euro-Dollar-0xa4ccd3b6daa763f729ad59eae75f9cbff7baf2cd/issues/84
Type: hats-finding

## Details
**Github username:** @itsabinashb
**Twitter username:** itsabinashb
**Submission hash (on-chain):** 0xeafcb7a625760ac3151eb9bf15ec8b6114d11ffcd10320e28413713fe1b5821d
**Severity:** medium

**Description:**
## Description
A malicious BLACKLISTER_ROLE can temporarily DoS the burning mechanism of USDE i.e EuroDollar by
blacklisting `address(0)`.
This occrurs due to logic of `isValid()`.  The function says:
- if 'from' & 'to' are both blacklisted then it will return false
- if 'from' is whitelisted & 'to' is blacklisted then it will return false.

So, we know that during `_burn()` call token is transferred to `address(0)`. As the 
`USDE::_update()` was modified where the function checking if the tx is valid or not using `Validator::isValid()`, here it will return false if `address(0)` is blacklisted i.e the burn will fail. 

## POC
- https://github.com/hats-finance/Euro-Dollar-0xa4ccd3b6daa763f729ad59eae75f9cbff7baf2cd/blob/c04ebafc3c6c48d612eb8df38ebd3e5b2ffa73a6/src/USDE.sol#L89
- https://github.com/hats-finance/Euro-Dollar-0xa4ccd3b6daa763f729ad59eae75f9cbff7baf2cd/blob/c04ebafc3c6c48d612eb8df38ebd3e5b2ffa73a6/src/Validator.sol#L130
