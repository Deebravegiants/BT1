# [C] C-04 | ExitVault Overcollects GMX/GLP Tokens From Users

## Summary
Severity: Critical
Contest weight: 0.3966
Dataset id: 2013
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the ExitVault contract, users are required to deposit GMX tokens to vest esGMX tokens. The intention is
that users contribute the precise amount of GMX needed to vest a corresponding amount of esGMX, based on the
vesting mechanics defined by the GMX protocol.
However, the current implementation in the ExitVault miscalculates the required amount of GMX, and therefore, forces
the users to deposit more GMX tokens than necessary. The core of the issue lies in the _depositWithGmx function
within the ExitVault contract, which determines the amount of esGMX to vest (esGmxToVest) based on the user's GMX
deposit. The calculation is as follows:
(uint256 maxVestWithGMX, uint256 maxGMXCapacity, uint256 maxGLPCapacity) =
getMaxVestAmountForVault(address(this)); uint256 esGmxToVest = (_amount * maxVestWithGMX) /
maxGMXCapacity;
This formula attempts to proportionally assign esGMX to vest based on the amount of GMX deposited. However, it
does not accurately reflect the vesting requirements defined in the GMX Vester contract, specifically the
getPairAmount function, which calculates the exact amount of GMX required to vest a given amount of esGMX.
In the GMX Vester contract, the getPairAmount function ensures that the amount of GMX needed is proportional to the
user's combined average staked amount and the maximum vestable amount of esGMX, following this formula:
pairAmount = esAmount * combinedAverageStakedAmount / maxVestableAmount;
By not aligning with this formula, the ExitVault overestimates the amount of GMX needed for vesting. This results in
users depositing more GMX tokens than required. Users are locking up excess GMX without receiving additional
vesting benefits, which is inefficient and can discourage participation.
The overcollection not only misaligns user expectations but also contradicts the protocol's goal of optimizing resource
utilization. Users contribute more capital than necessary and the excess GMX remains idle within the vault, providing
no additional advantage in terms of vesting esGMX. This same concept also affects the GLP/GLPVester flow.

## Recommendation
To resolve this issue, the ExitVault contract should be modified to accurately calculate the required amount of GMX
needed to vest the available esGMX, directly reflecting the logic used in the GMX Vester contract's getPairAmount
function.
The _depositWithGmx function should be updated to use the correct formula for determining esGmxToVest. This
involves calculating the amount of esGMX that can be vested based on the amount of GMX deposited, the combined
average staked amount, and the maximum vestable amount, as per the Vester's logic.
