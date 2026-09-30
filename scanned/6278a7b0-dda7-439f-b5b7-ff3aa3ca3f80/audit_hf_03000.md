# [M] `Project.changeOrder`

## Summary
Severity: Medium
Contest weight: 0.4385
Dataset id: 16740
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[Project.sol#L402](https://github.com/code-423n4/2022-08-rigor/blob/5ab7ea84a1516cb726421ef690af5bc41029f88f/contracts/Project.sol#L402)  

The `changeOrder()` function will revert when it’s called for the tasks that don’t have subcontractors.

As a result, the project builder and contractor can’t change the cost of a task until the subcontractor is confirmed.

## Proof of Concept
The `changeOrder()` is used to change the cost or subcontractor of a task and there is no documentation that this function must be called only after a subcontractor is confirmed.

Also, it’s reasonable to be able to change the cost when a subcontractor isn’t confirmed yet.

But when it checks signature [here](https://github.com/code-423n4/2022-08-rigor/blob/5ab7ea84a1516cb726421ef690af5bc41029f88f/contracts/Project.sol#L402), it assumes the task has a confirmed subcontractor already and `checkSignatureTask()` will revert in other cases.

So this function will be useless for non SCConfirmed tasks.

## Recommendation
We should check separately in case the subcontractor is confirmed or not [here](https://github.com/code-423n4/2022-08-rigor/blob/5ab7ea84a1516cb726421ef690af5bc41029f88f/contracts/Project.sol#L402).

```solidity
if (getAlerts(_taskID)[2]) {
    // If subcontractor has confirmed.
    checkSignatureTask(_data, _signature, _taskID);
} else {
    // If subcontractor not has confirmed.
    checkSignature(_data, _signature);
}
```

I think this is invalid, since _currently_ `checkSignatureTask` will pass if SC is the zero address and the signature isn’t a valid signature (i.e. builder and GC can just pass zero as the signature).

This will only be valid if the sponsor fixes other bugs by making `checkSignatureValidity()` revert on invalid signature.

Will downgrade to Medium given this is a feature being malfunctioning.
