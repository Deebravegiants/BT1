# [M] Suggested Adherence of Checks-Eﬀects-Interactions

## Summary
Severity: Medium
Contest weight: 0.4620
Dataset id: 12717
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A common coding best practice in Solidity is the adherence of checks-effects-interactions principle. This principle is eﬀective in mitigating a serious attack vector known as re-entrancy. Via this particular attack vector, a malicious contract can be reentering a vulnerable contract in a nested manner. Speciﬁcally, it ﬁrst calls a function in the vulnerable contract, but before the ﬁrst instance of the function call is ﬁnished, second call can be arranged to re-enter the vulnerable contract by invoking functions that should only be executed once. This attack was part of several most prominent hacks in Ethereum history, including the DAO [16] exploit, and the Uniswap/Lendf.Me hack [15].
We notice occasions where the checks-effects-interactions principle is violated.
Using the ARBRewarder as an example, the _calculateAndSendARB() function (see the code snippet below) is provided to externally call a rewarder contract to transfer assets. However, the invocation of an external contract requires extra care in avoiding the above re-entrancy.
Apparently, the interaction with the external contract (line 129) starts before eﬀecting the update on internal state (line 132), hence violating the principle. In this particular case, if the external contract has certain hidden logic that may be capable of launching re-entrancy via the very same function. Note that there is no harm that may be caused to current protocol. However, it is still suggested to follow the known checks-effects-interactions best practice.
```solidity
function _calculateAndSendARB(address _stakingToken, address _rewarder) internal {
    if (_rewarder == address(0)) return;
    PoolInfo storage pool = tokenToPoolInfo[_stakingToken];
    if (!pool.isActive || pool.ARBPerSec == 0) return;
    uint256 multiplier = block.timestamp - pool.lastRewardTimestamp;
    if (block.timestamp >= pool.endTimestamp) {
        pool.isActive = false;
        multiplier = pool.endTimestamp - pool.lastRewardTimestamp;
    }
    uint256 rewardAmount = (multiplier * pool.ARBPerSec);
    rewardAmount = Math.min(rewardAmount, ARB.balanceOf(address(this)));
    ARB.approve(_rewarder, rewardAmount);
    IBaseRewardPool(_rewarder).queueNewRewards(rewardAmount, address(ARB));
    emit ARBRewadsSent(_stakingToken, _rewarder, rewardAmount, pool.lastRewardTimestamp, pool.ARBPerSec);
    pool.lastRewardTimestamp = block.timestamp;
}
```
In the meantime, we should mention that the supported tokens in the protocol do implement rather standard ERC20 interfaces and their related token contracts are not vulnerable or exploitable for re-entrancy.

## Recommendation
Apply necessary reentrancy prevention by following the checks-effects-interactions best practice. Note other routines MasterPenpie::_withdraw() and VLPenpie::transferPenalty() can be similarly improved.
