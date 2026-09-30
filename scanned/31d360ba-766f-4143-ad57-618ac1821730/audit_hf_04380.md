# [M] M-08 | Incorrect Access Control For setTotalUsdcInTreasure

## Summary
Severity: Medium
Contest weight: 0.0396
Dataset id: 21596
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an incorrect access‑control configuration on the function that updates the recorded amount of USDC held in the protocol treasury. The function setTotalUsdcInTreasure was intended to be callable only by accounts that possess the DEFAULT_ADMIN_ROLE, which represents the highest level of governance authority. However, the contract mistakenly grants the TREASURE_UPDATER_ROLE permission to invoke this function. The root cause is a mismatched onlyRole modifier that does not enforce the intended admin‑only restriction. Because the TREASURE_UPDATER_ROLE is also used by the dailyUsdcNetFeeRevenue routine, which includes signature verification and timestamp checks, allowing this role to call setTotalUsdcInTreasure bypasses those protective checks. An attacker who can acquire the TREASURE_UPDATER_ROLE—through a compromised key, delegated permission, or any other means—can call setTotalUsdcInTreasure and arbitrarily set the total USDC balance reported by the contract. This manipulation can corrupt accounting, inflate or deflate the treasury balance, and consequently affect downstream fee calculations, reward distributions, and any logic that relies on the correct treasury total. Users may notice symptoms such as unexpected zero balances, missing fee rewards, or rewards that appear larger than expected, because the protocol’s accounting assumptions are violated. The issue manifests whenever setTotalUsdcInTreasure is invoked, which under normal operation should be restricted to the admin role but is currently exposed to a lower‑privileged role. The bug was discovered during a manual security audit when the auditor observed that the access‑control modifier did not match the documented design. It can be hard to notice because the function itself may appear to work correctly and the role mismatch does not produce an immediate runtime error; the impact only becomes visible through incorrect accounting outcomes. To remediate the issue, the access‑control modifier on setTotalUsdcInTreasure should be changed to require onlyRole(DEFAULT_ADMIN_ROLE), ensuring that only the designated admin can modify the treasury total, and any additional validation logic from dailyUsdcNetFeeRevenue should be retained for functions that require it. This correction restores the intended governance hierarchy and prevents unauthorized manipulation of treasury accounting.

## Recommendation
Update the access control modifier in setTotalUsdcInTreasure to use onlyRole(DEFAULT_ADMIN_ROLE)
