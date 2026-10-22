# [C] Incorrect Time Validation in unstake Function leads to permanent lock of the staked funds

## Summary
Severity: Critical
Contest weight: 0.7402
Dataset id: 5764
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The unstake function is designed to allow unstaking only after 12 months from the stake start time. However, the current time validation logic incorrectly multiplies the seconds in a year by the number of claimed months, leading to an excessive required time delay.
```solidity
let enlapsed_time = Clock::get()?.unix_timestamp - self.position.start_time;
// < SECONDS_IN_A_YEAR
if enlapsed_time
< SECONDS_IN_A_YEAR
.checked_mul(
(self.position.claimed as i64)
.checked_add(1)
.ok_or(Overflow)?,
)
.ok_or(Overflow)?
{
return Err(ErrorCode::NotEnoughTimeElapsed.into());
}
```
If a user claims rewards for 6 months and later tries to unstake after 12 months, the function would require over 7 years to elapse, resulting in a significant loss of funds.

## Recommendation
Modify the validation logic to check only for a minimum of 12 months (1 year) elapsed time:
```solidity
let enlapsed_time = Clock::get()?.unix_timestamp - self.position.start_time;
// < SECONDS_IN_A_YEAR
if enlapsed_time < SECONDS_IN_A_YEAR {
return Err(ErrorCode::NotEnoughTimeElapsed.into());
}
```
