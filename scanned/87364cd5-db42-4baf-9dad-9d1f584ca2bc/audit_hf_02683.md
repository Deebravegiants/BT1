# [H] DoS In StakeUserETHToBeaconChain() Due To Forced ETH Transfer Through SelfDestruct

## Summary
Severity: High
Contest weight: 0.2405
Dataset id: 14540
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function stakeUserETHToBeaconChain() incorporates an assert statement - assert(address(this).balance == 0), at its termination on line [155], to verify that all ETH sent from the pool manager has been transferred to the beacon chain. However, the calculation of ETH is dependent on the msg.value received from the pool manager, which makes the assumption that the ETH balance in PermissionlessPool is zero prior to the function call.
While PermissionlessPool would typically revert in the fallback() function with UnsupportedOperation() if any ETH is transferred to the contract, there’s an unhandled case where ETH is forcibly sent to the contract through a self-destruct operation. This undermines the assumption that PermissionlessPool will retain no funds prior to invoking stakeUserETHToBeaconChain().
In a scenario where an attacker forcibly sends a small amount (1 wei) of ETH to PermissionlessPool via self destruct, the function stakeUserETHToBeaconChain() would always revert due to the assert statement at its end.

## Recommendation
The testing team recommends removing this assert statement.
