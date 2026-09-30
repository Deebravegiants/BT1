# [H] setSherlockCoreAddress can be frontruned.

## Summary
Severity: High
Chain: Smart contract
Component: 2022-01-sherlock
Published: 2022-01-23
Source: https://github.com/code-423n4/2022-01-sherlock-findings/issues/83
Type: code-finding

## Details
# Handle

wuwe1


# Vulnerability details

## Proof of Concept
`SherDistributionManager.sol` and `AaveV2Strategy.sol` are affected by this.

For sdm, attacker can monitor mempool and frontrun the `setSherlockCoreAddress` . By setting the `sherlockCore` as a address controlled by attacker. Attacker can call `pullReward` and send arbitrary amount of `sher` in sdm to the attacker. This effectively causing a DOS attack on sdm.

For AaveV2Strategy.sol , attacker can call withdrawAll and drain the underlying assert if there is any.

## Recommended Mitigation Steps

Call setSherlockCoreAddress in inheriting contract's constructor.
