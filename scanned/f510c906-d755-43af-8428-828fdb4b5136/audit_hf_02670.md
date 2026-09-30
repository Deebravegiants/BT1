# [M] Incorrect stakedButNotVerifiedEth Accounting Can Overinﬂate TVL

## Summary
Severity: Medium
Contest weight: 0.2646
Dataset id: 14453
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The OperatorDelegator contract maintains a counter for stakedButNotVerifiedEth. This counter tracks ETH staked on the beacon chain for validators that have not veriﬁed their withdrawal credentials on EigenPod. However, several situations arise where stakedButNotVerifiedEth does not correctly decrement back to 0, causing the OperatorDelegator’s staked ETH balance to be overinﬂated. This directly impacts TVL calculations used which are used to determine the ezETH/ETH mint rate.
The OperatorDelegator::stakeEth() function increments the stakedButNotVerifiedEth state variable to account for ETH that has been staked into a validator but has not had its withdrawal credentials veriﬁed on the EigenPod.
stakedButNotVerifiedEth is later decremented by the validator’s current eﬀective balance when the validator’s withdrawal credentials are veriﬁed, since the staked ETH will be accounted for inside the OperatorDelegator's podOwnerShares balance in EigenPodManager.
However, scenarios can arise where stakedButNotVerifiedEth is not correctly decremented back to 0 due to the validator’s current eﬀective balance being less than stakedButNotVerifiedEth. These scenarios are listed below:
1. Natively restaking more than 32 ETH into a single validator.
2. Verifying withdrawal credentials with a validator eﬀective balance of less than 32 ETH either by:
   a. Submitting withdrawal credentials after the validator has exited.
   b. Any penalties that decrease validator eﬀective balance below 32 ETH.
The ﬁrst scenario would be achieved by calling DepositQueue::stakeEthFromQueue() with the same arguments more than once, increasing stakedButNotVerifiedEth above 32 ETH. A validator’s eﬀective balance is capped at 32 ETH, (MAX_EFFECTIVE_BALANCE), resulting in stakedButNotVerifiedEth not being decremented back to 0. Any ETH above MAX_EFFECTIVE_BALANCE will be partially withdrawn through DelayedWithdrawalRouter and sent back to the DepositQueue to be included in Renzo’s TVL calculation again. This means that the extra ETH from subsequent staking attempts is double-counted in TVL.
The second scenario occurs if the validator has exited before its withdrawal credentials are veriﬁed in EigenPod. In this case, validatorCurrentBalanceGwei = 0 and hence stakedButNotVerifiedEth is not decremented.
Once the validator’s full withdrawal has been processed via OperatorDelegator::verifyAndProcessWithdrawals(), the OperatorDelegator's podOwnerShares will be credited with the 32 ETH amount that was initially staked, resulting in the 32 ETH being double-counted in TVL.
In a similar but less severe scenario, penalties such as inactivity can cause a validator's eﬀective balance to drop below 32 ETH and stakedButNotVerifiedEth from being correctly decremented back to 0. Additionaly, it is worth mentioning that due to hysteresis, a validator’s actual balance only needs to decrease below 31.75 ETH for the eﬀective balance Restaking Smart Contract Review to decrease to 31 ETH. Conversely, the validator’s actual balance needs to increase above 32.25 ETH for the eﬀective balance to recover back to 32 ETH. This lack of precision in validator eﬀective balance also leads to inaccuracies in stakedButNotVerifiedEth accounting that cause misrepresentations in TVL.

## Recommendation
To prevent the ﬁrst scenario, consider adding checks to make sure that a staker does not get natively restaked into the same validator more than once.
One way to ensure this is to keep track of all validatorPubkeys that have been staked into in DepositQueue.
To prevent the second category of scenarios, consider keeping a mapping of each validator's stakedButNotVerifiedEth value instead of using one global variable.
When OperatorDelegator::verifyAndProcessWithdrawals() is called, reset the veriﬁed validator's stakedButNotVerifiedEth value back to 0 instead of decrementing it by validatorCurrentBalanceGwei.
