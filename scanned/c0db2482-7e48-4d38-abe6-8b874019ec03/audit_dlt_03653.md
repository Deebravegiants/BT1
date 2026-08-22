# [M] The node operators are likely to be slashed in an unfair way

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-02-gogopool-mitigation-contest
Published: 2023-02-14
Source: https://github.com/code-423n4/2023-02-gogopool-mitigation-contest-findings/issues/23
Type: code-finding

## Details
# Lines of code

https://github.com/multisig-labs/gogopool/blob/4bcef8b1d4e595c9ba41a091b2ebf1b45858f022/contracts/contract/MinipoolManager.sol#L464


# Vulnerability details

# C4 issue

H-04: [Hijacking of node operators minipool causes loss of staked funds](https://github.com/code-423n4/2022-12-gogopool-findings/issues/213)

# Comments
In the original implementation, the protocol had some unnecessary state transitions and it was possible for node operators to interfere the recreation process.
The main problem was the `recordStakingEnd()` and `recreateMiniPool()` were separate external functions and the operator could frontrun the `recreateMiniPool()` and call `withdrawMinipoolFunds()`.

# Mitigation
[PR #23](https://github.com/multisig-labs/gogopool/pull/23)
The mitigation added a new function `recordStakingEndThenMaybeCycle()` and handled `recordStakingEnd()` and `recreateMiniPool()` in an atomic way.
With this mitigation, the state flow is now as below and it is impossible for a node operator to interfere the recreation process.
![Imgur](https://imgur.com/JCoiCvl.jpg)
But this mitigation created another minor issue that the node operators have risks to be slashed in an unfair way.

# New issue
The node operators are likely to be slashed in an unfair way

# Code snippet
https://github.com/multisig-labs/gogopool/blob/4bcef8b1d4e595c9ba41a091b2ebf1b45858f022/contracts/contract/MinipoolManager.sol#L464

# Proof of concept
In the previous implementation, I assumed rialtos are smart enough to recreate minipools only when it's necessary.
But now, the recreation process is included as an optional way in the `recordStakingEndThenMaybeCycle()`, so as long as the check `initialStartTime + duration > block.timestamp` at L#464 passes, recreation will be processed.

Now let us consider the timeline. One validation cycle in the whole sense contains several steps as below.
![Imgur](https://imgur.com/p6xWqgC.jpg)

1) Let us assume it is somehow possible that `startTime[1] > endTime[0]`, i.e., the multisig failed to start the next cycle at the exact the same timestamp to the previous end time. This is quite possible due to various reasons because there are external processes included.
In this case the timeline will look as below.
![Imgur](https://imgur.com/e292GIO.jpg)

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-02-gogopool-mitigation-contest-findings/issues/23_
