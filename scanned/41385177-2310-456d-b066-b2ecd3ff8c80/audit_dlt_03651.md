# [M] `amountAvailableForStaking()` not fully utilized with `compoundedAvaxNodeOpAmt` easily forfeited

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-02-gogopool-mitigation-contest
Published: 2023-02-14
Source: https://github.com/code-423n4/2023-02-gogopool-mitigation-contest-findings/issues/52
Type: code-finding

## Details
# Lines of code

https://github.com/multisig-labs/gogopool/blob/3b5ab1d6505ef9be6197c4056acd38d6bed4aff6/contracts/contract/tokens/TokenggAVAX.sol#L134-L146
https://github.com/multisig-labs/gogopool/blob/3b5ab1d6505ef9be6197c4056acd38d6bed4aff6/contracts/contract/MinipoolManager.sol#L497-L505


# Vulnerability details

## Impact
The mitigated step is implemented at the expense of economic loss to both the node operators and the liquid stakers if `compoundedAvaxNodeOpAmt <= ggAVAX.amountAvailableForStaking()`.

## Proof of Concept
Here is a typical scenario:

1. The protocol now assumes that a 1:1 nodeOp:liqStaker funds ratio is guaranteed to be met because of the atomic transaction that has also been implemented.
2. This is deemed an edge case that will only be optimally utilized if `compoundedAvaxAmt == ggAVAX.amountAvailableForStaking()`.
3. The atomic transaction is going to fail if `compoundedAvaxAmt > ggAVAX.amountAvailableForStaking()` after all due to situations like liquid stakers have been actively calling [`withdrawAVAX()`](https://github.com/multisig-labs/gogopool/blob/3b5ab1d6505ef9be6197c4056acd38d6bed4aff6/contracts/contract/tokens/TokenggAVAX.sol#L196-L205).

Under normal circumstances, [`ggAVAX.amountAvailableForStaking()`](https://github.com/multisig-labs/gogopool/blob/3b5ab1d6505ef9be6197c4056acd38d6bed4aff6/contracts/contract/tokens/TokenggAVAX.sol#L134-L146) is going to be adequate enough to cater for `compoundedAvaxNodeOpAmt`. This should not be easily forfeited without first checking whether or not `ggAVAX.amountAvailableForStaking()` is greater than `compoundedAvaxNodeOpAmt`.

## Tools Used
Manual inspection

## Recommended Mitigation Steps
Consider implementing the following check in `recreateMinipool()` to get the best out of it:

[File: MinipoolManager.sol#L486-L517](https://github.com/multisig-labs/gogopool/blob/3b5ab1d6505ef9be6197c4056acd38d6bed4aff6/contracts/contract/MinipoolManager.sol#L486-L517)

```diff
	function recreateMinipool(address nodeID) internal whenNotPaused {
		int256 minipoolIndex = onlyValidMultisig(nodeID);
		Minipool memory mp = getMinipool(minipoolIndex);
		MinipoolStatus currentStatus = MinipoolStatus(mp.status);

		if (currentStatus != MinipoolStatus.Withdrawable) {
			revert InvalidStateTransition();
		}

```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-02-gogopool-mitigation-contest-findings/issues/52_
