# [C] C-01 | User Info Not Updated During Matching

## Summary
Severity: Critical
Contest weight: 0.3410
Dataset id: 2023
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the matchWithdrawRequest function, the matcher's shares are incremented without first invoking the
_depositGMX or _depositGLP functions. This prevents the wethRewardDebt from being updated. As a result, the s.userInfo[matcher].glpStream.lastClaim mapping remains unchanged for the matcher, even though his s.userInfo[matcher].glpStream.shares have increased.
In the GMXYieldStrategy contract, when updating the matcherInfo during position matching, the contract
only updates the shares field in the gmxStream structure but fails to update the corresponding esGMX
vesting information.
This results in several issues such as a permanent DoS or drained funds. Furthermore, The WETH reward
calculation can underflow if the share amount decreased since the last claim.
Here we can see the reward calculation:
uint256 pendingWeth = shares * s.accumulatedTokensPerShare / 1e18 - wethRewardDebt;
Therefore an underflow DoS occurs if:
shares * s.accumulatedTokensPerShare / 1e18 < wethRewardDebt
The WETH reward debt is calculated in the same way:
wethRewardDebt = shares * s.accumulatedTokensPerShare / 1e18;
That means if a wethRewardDebt is stored, the shares amount of the user decreases and it tries to calculate
the pendingWeth amount again resulting in an underflow DoS. A decrease in shares can happen regularly
when users withdraw their tokens.
If a user withdraws half their tokens a DoS of the system occurs for this user until the user's rewards are doubled which could never happen if the owner exits the system in the meantime.

## Recommendation
Be sure to update all relevant values such as the GMX shares, esGMX vesting information as well as
recalculating the wethRewardDebt when processing matcher info. Use the _depositGMX or _depositGLP
function to claim the pending rewards of the matcher, updating his userInfo before increasing his shares.
Additionally, save the accumulated amount instead of the debt in the user struct and then calculate the users
share of the stake based on the difference between the current accumulated amount and the saved one.
