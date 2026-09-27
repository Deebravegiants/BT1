# [M] Stake can be withheld indefinitely

## Summary
Severity: Medium
Source: https://github.com/UMAprotocol/protocol/blob/7938617bf79854811959eb605237edf6bdccbc90/packages/core/contracts/oracle/implementation/Staker.sol
Type: audit-issue

## Details
In the [Staker](https://github.com/UMAprotocol/protocol/blob/7938617bf79854811959eb605237edf6bdccbc90/packages/core/contracts/oracle/implementation/Staker.sol) contract the function [setUnstakeCoolDown](https://github.com/UMAprotocol/protocol/blob/7938617bf79854811959eb605237edf6bdccbc90/packages/core/contracts/oracle/implementation/Staker.sol#L243) allows the contract owner to set the `unstakeCoolDown` variable to an arbitrarily large `uint64` value. This variable controls the time that needs to pass between successful calls to `requestUnstake` and `executeUnstake`. It retroactively applies changes to all users currently within the cooldown phase.

Giving the contract owner full control over setting `unstakeCoolDown` violates the trust assumptions typically present in a staking system. Namely, stakers expect to be able to retrieve their stake regardless of operator error or operator malice. Setting `unstakeCoolDown` to a very large value would render each user’s stake practically unretrievable.

The intended use of this contract is to be owned by the `GovernorV2` contract thereby allowing the affected stakers to control the `unstakeCoolDown` through governance proposals, which reduce the likelihood of malice. However, voters who disagree with a legitimate majority vote to extend `unstakeCoolDown` will most likely not be able to leave the staking system before the changes take effect.

Consider validating the input of the `setUnstakeCoolDown` function against an acceptable maximum cooldown time. Also consider allowing the retroactive application of a new `unstakeCoolDown` value only in cases when it acts to decrease the cooldown time of users who are actively unstaking.

**Update:** _Acknowledged. UMA indicated that the economic incentives between stakeholders make this scenario unlikely. The increased complexity and gas cost of the suggested recommendation does not appear justified._
