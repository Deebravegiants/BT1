# [M] Long time delay between transactions causes

## Summary
Severity: Medium
Contest weight: 0.2612
Dataset id: 23028
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Protocol Q&A mentions the RESERVE address:
There is a RESERVE address to which a portion of all interest accrues. It should be able to take any action and behave normally.
However, when RESERVE address receives its portion of all interest, it also receives rewards, but the rewards are calculated incorrectly, adding less rewards to RESERVE than it should receive, thus the RESERVE account loses rewards. This happens because RESERVE receives its portion of all interest continuously (each second), but the rewards are calculated with RESERVE balance only at the start of the interval (RESERVE balance at the time of last transaction) ignoring any RESERVE balance accural inside the interval.
Example: transaction at t=0: RESERVE balance = 0, reward rate = 1 per second per unit balance, total borrows increases at such a rate, the RESERVE receives 10 new tokens per second. t=1: RESERVE balance = 10, rewards should be 0 (not updated in storage) t=2: RESERVE balance = 20, rewards should be 10 (not updated in storage) t=3: RESERVE balance = 30, rewards should be 10+20=30 (not updated in storage) t=4: RESERVE balance = 40, rewards should be 30+30=60 (not updated in storage). Transaction at t=5: first the rewards are updated for the time interval [0;5] with the stored balance (0), so RESERVE rewards are 0, only then the RESERVE balance is set to 50.
RESERVE receives its portion of all interest by minting new shares:
/Lender.sol#L527
However, when minting, the rewards are calculated by multiplying user's balance before the mint by the accumulated rewards per unit balance:
lob/main/aloe-ii/core/src/libraries/Rewards.sol#L92
This is correct for all accounts except RESERVE: all accounts have static balances between updates, so the rewards formula is correct, but RESERVE has continously increasing balance over time, meaning the formula to calculate the reward should take this into account, but it doesn't.
Internal pre-conditions
Always happens by itself, the longer the time between transactions, the larger the rewards loss for the RESERVE account.
External pre-conditions
None
Attack Path
None, always happens by itself.
RESERVE account always losing rewards, the longer the time between transactions, the larger the rewards loss. For example, if the protocol has $10M borrowed at the rate of APR of 10%, and reserve factor is 10%, this means that RESERVE account receives $0.003 per second. Let's say there is a reward at the rate of 1 reward token per unit balance per second. Then:
• if transactions are going every second for 1 hour, the RESERVE account receives reward of 0.003 * (0 + 1 + 2 + 3 + 4 + ... + 3599) = 0.003 * 6478200 = 19434.6 tokens (this is the correct amount it should receive)
• if there are just 2 transactions (at t = 0 and at t = 1 hour), then RESERVE account receives reward of 0. If both scenarios continue for 1 day (transactions every second vs every 1 hour), then in scenario 1 the RESERVE account will receive 11.197M tokens, in scenario 2 the RESERVE account will receive 10.731M tokens, a loss of 466K reward tokens or a 4.3% loss.
The RESERVE account total rewards accured in time is quadratic, while the rewards loss is linear in time, so the longer time period, the higher the absolute loss and the smaller the relative (percentage) loss.

## Recommendation
When minting portion of percentage to RESERVE account, handle the rewards accumulation in a different way - use the simple arithmetic progression formula both when accumulating global rewards (linearly increasing totalSupply) and RESERVE user's rewards (linearly increasing balance). In reality the totalSupply and balance growth is exponential (but very close to linear in small intervals), but this might not be worth the effort since the error between linear and exponential growth calculations will be very tiny.
