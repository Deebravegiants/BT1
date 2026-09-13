# [M] initializeAuction()  need to prevent repeated call in the same epoch

## Summary
Severity: Medium
Reporter: bin2chen
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L211
Type: audit-issue

## Details
# initializeAuction()  need to prevent repeated call in the same epoch

## Summary
Although initializeAuction() has  onlyKeeper restriction, but it is no guarantee that the call will not be repeated, causing "actionProcessed" back to false,“startTime“ be reset and so on problems

## Vulnerability Detail

## Impact

## Code Snippet

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L211

## Tool used

Manual Review

## Recommendation
```solidity
    function initializeAuction() external onlyKeeper {
        VaultStorage.Layout storage l = VaultStorage.layout();
        VaultStorage.Option memory option = _setOptionParameters(l);


+        require(l.startTime==0 || l.auctionProcessed,"bad old auction status");
```
