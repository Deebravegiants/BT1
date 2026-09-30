# [M] claimAllGas claims gas at a loss

## Summary
Severity: Medium
Contest weight: 0.1817
Dataset id: 1870
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
claimAllGas claims less gas than claimMaxGas, the difference will be sent to Blast as fees, resulting in a loss for the protocol.
Blast has a special gas mechanic where contract can claim some percentage of the gas they use. They can do that instantly for 50% of the funds, or wait up to a month in order to linearly unlock 100% of the used gas. In short, if a user uses 1 ETH worth of gas at time T, then at:
1. At T the contract can claim 50%, or 0.5 ETH
2. At T + 2 weeks the contract can claim 75% or 0.75 ETH
3. At T + 1 month the contract can claim 100% or 1 ETH
All contracts claim their gas using claimAllGas, however this function claims 100% of the gas, while paying the fees for the one that is not fully unlocked, i.e. claiming all the gas, even if it' not fully unlocked. This means that every time the admin calls claimAllGas the system loses some percentage of all gas that was used inside the contracts for up to 1 month prior.
Example:
1. User uses 1 ETH worth of gas at T
2. User uses 1 ETH worth of gas at T + 1 month
3. Admin calls claimAllGas
Now the system will claim the first 1 ETH, but only claim 50% of the second one and send the other 50% to Blast as fees for early claim, resulting in 1.5 ETH instead of 2.
Less gas will be claimed.

## Recommendation
Add a function to call claimMaxGas and use it instead. This function will claim all of the gas that is vested at 100% and leave the rest to continue vesting, which will result in claim rate of 100% every time. Blast docs for extra info (if needed).
