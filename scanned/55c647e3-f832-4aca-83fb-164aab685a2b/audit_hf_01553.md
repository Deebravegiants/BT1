# [H] Functions cannot be called

## Summary
Severity: High
Contest weight: 0.7565
Dataset id: 8299
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The YieldToken implementation is created within the YieldTokenFactory constructor:
```solidity
constructor(address _fyde, address _relayer) {
    TOKEN_IMPLEMENTATION = address(new YieldToken(address(this), _fyde, _relayer));
}
```
The YieldManager contract inherits from the YieldTokenFactory contract:
```solidity
constructor() YieldTokenFactory(_fyde, _relayer) Ownable(msg.sender) ERC1967Proxy(_stratgies, "") {}
```
Therefore, the YieldManager will be the owner of the YieldToken implementation since it will be the msg.sender and thus the owner of the implementation:
```solidity
constructor(address _yieldManager, address _fyde, address _relayer) Ownable(msg.sender) {
    yieldManager = _yieldManager;
    fyde = _fyde;
    relayer = _relayer;
    baseYieldToken = IYieldToken(address(this));
}
```
The issue is that the YieldToken contract contains two functions that can only be called by the owner (i.e., the YieldManager):
```solidity
function setYieldManager(address _yieldManager) public onlyOwner {
    yieldManager = _yieldManager;
}

function setRelayer(address _relayer) public onlyOwner {
    relayer = _relayer;
}
```
However, the YieldManager cannot call these functions as there is no mechanism provided to do so.

## Recommendation
Consider transferring ownership of the YieldToken implementation to the YieldManager.owner().
