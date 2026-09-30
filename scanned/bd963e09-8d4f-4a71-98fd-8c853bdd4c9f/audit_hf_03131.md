# [M] dispute() can only be called by root

## Summary
Severity: Medium
Contest weight: 0.3907
Dataset id: 17616
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
dispute() -> _settleDispute() -> blockCaller() requires root access, thus dispute() requires root access.  
Oct 3rd to Oct 5th.  
The internal function blockCaller() can only be called by root because of the callerIsRoot modifier:  
https://github.com/fiatdao/fiat/blob/b8406c29638b9f6e598ad6d961583df5b0a719a5/src/utils/Guarded.sol#L62-L72  
```solidity
function blockCaller(bytes32 sig, address who) public override callerIsRoot {
    _canCall[sig][who] = false;
    emit BlockCaller(sig, who);
}
```
OptimisticOracle.sol#L280 calls the internal function blockCaller(), which makes the whole dispute() function only callable by root.  
dispute() is no longer a permissionless method.

## Recommendation
Consider changing to this.blockCaller() and grant the contract itself root access.  
was added and is used in _settleDispute()
