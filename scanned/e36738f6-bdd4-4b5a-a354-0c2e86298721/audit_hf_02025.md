# [M] Possible Front-Running Resulting Losing Ownership

## Summary
Severity: Medium
Contest weight: 0.3996
Dataset id: 11555
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The 88mph protocol is a fixed-rate yield-generation protocol which pools the deposits together. It puts the deposited DAI into a single pool, from which users can withdraw a deposit once its deposit period is over. Users will receive MPH tokens after deposits from MPHToken contract. After the MPHToken contract is deployed, the init() function will be called to initialize the contract and announce ownership.
```solidity
function init() public {
    require(!initialized, "MPHToken: initialized");
    initialized = true;
    _transferOwnership(msg.sender);
}
```
However, the init function is defined as public and anyone can call this function to take the ownership of MPHToken. As a result, right after the MPHToken contract is deployed, an attacker can use high gas fee to init() the contract first. This would cause front-running and no one is able to take back the ownership anymore.

## Recommendation
Use onlyOwner for init() function.
