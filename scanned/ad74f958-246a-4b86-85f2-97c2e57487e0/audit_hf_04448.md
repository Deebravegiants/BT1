# [M] Staking rewards susceptible to reward multiplier manipulation

## Summary
Severity: Medium
Contest weight: 0.2618
Dataset id: 21939
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
For staking in the Chainlink Operator and Community staking pools a staker is rewarded through the Chainlink [RewardVault](https://etherscan.io/address/0x996913c8c08472f584ab8834e925b06D0eb1D813). Here rewards are accrued per time staked.

There is however a twist to how the rewards work compared to the standard rewards design. To promote staying in your position for an extended period of time, Chainlink uses a `multiplier`. This goes from 0 to 1 over a period of 90 days (at time of writing). Just as you start staking you have a multiplier of 0, then it linearly increases to 1 over 90 days.

Were you to unstake during this period, the multiplier is reset and the forfeited rewards you should have earned are distributed to the other stakers.

This can be used to grief LinkPool stakers to reduce their rewards received rewarding stakers outside of LinkPool.

A user could iterate depositing a full vault (+ 1 LINK) and withdrawing a full vault to iterate through the whole current vault group. Thus resetting all the multipliers for the vaults.

A quick overview of the impact using current numbers from the community pool:

Current emission rate for community stakers is `~0.05 LINK/s`. The community vault is currently full with a total of `40875000 LINK` staked. This gives a gain per token per second of `0.05 / 40875000 =~ 1.2e-09`

LinkPool has a total stake `1324452 LINK`, ~3% of the pool.

As mentioned above, the multiplier period is `90 days` and the unbonding period is `4 weeks` which is the fastest you can reset the multiplier.

This gives a reward calculation:
```
perTokenPerS*(staked*0.2)*4 weeks =~ 783 LINK
```
To get the total forfeited you'll need to multiply with `1-(staked time/multiplier period)`:
```
perTokenPerS*(staked*0.2)*4 weeks*(1 - (4 weeks/90 days)) =~ 540 LINK
```
Hence in this case a total of 540 LINK would be lost. Note that this only applies to when the vaults start from 0 multiplier. If a vault was previously at `>90 days` there wouldn't be any forfeit hence the gain is only gotten the second time you do this for a vault group. As it is only then the multiplier is completely reset.

To see the profitability of this, the gained `540 LINK` is split into the pool:
```
540/40875000 = 1.3e-5 per held link
```
If a user has 100 vaults (with maximum deposit 15000 LINK each), this would gain them a total of 19 LINK which is in the ballpark of what the gas would probably cost of this.

Hence the attack vector is pretty small. However there is still a possibility for griefing or un-intended loss of rewards due to vaults having their multiplier unnecessarily reset.

Note, that this is taken with the current community staking pool distribution. The attack grows more profitable the larger the LinkPool stake is.

## Recommendation
For the attack vector of resetting all the vaults multipliers it relies on being able to easily iterate through the vaults with deposits + withdrawals. This can be mitigated by implementing a small withdrawal timelock.

For the unintentional loss of rewards that can happen if you withdraw from vaults that have been staking for <90 days, consider enforcing a rotation of the `withdrawalIndex`. Right now any can be chosen but if it always increases (until it loops back) it will hopefully keep vaults "alone" for more than 90 days.
