# [M] Never use .transfer(). Use call instead.

## Summary
Severity: Medium
Reporter: peanuts
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueInternal.sol
Type: audit-issue

## Details
# Never use .transfer(). Use call instead.

## Summary

The function _redeem uses .transfer instead of call to transfer unredeemed share amount to the receiver. 

## Vulnerability Detail

The withdrawal will inevitably fail when: 

1. The withdrawer smart contract does not implement a payable fallback function.
2. The withdrawer smart contract implements a payable fallback function which uses more than 2300 gas units. 
3. The withdrawer smart contract implements a payable fallback function which needs less than 2300 gas units but is called through a proxy that raises the call’s gas usage above 2300.

## Impact

Transfer will fail if ever the recipient uses more than that gas. Use call() instead of transfer() when transferring eth. However, keep in mind to follow the checks-effects-interactions pattern to reduce the risk of reentrancy when using call() function.

## Code Snippet

```
128        // transfers unredeemed share amount to the receiver
129        require(Vault.transfer(receiver, unredeemedShares), "transfer failed");
```

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueInternal.sol

## Tool used

Manual Review

## Recommendation

Use call instead of transfer(). 

https://consensys.net/diligence/blog/2019/09/stop-using-soliditys-transfer-now/
