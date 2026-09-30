# [M] Lack of validation in deployTokenWithCustomParams function

## Summary
Severity: Medium
Contest weight: 0.2160
Dataset id: 8769
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The deployTokenWithCustomParams function in the Holofair contract allows creators to deploy tokens with custom presale parameters. However, it lacks critical validations that are present in the addPresaleParams function. Specifically, the function does not verify that the sum of dexAllocation, teamAllocation, and presaleAllocation equals totalSupply. This oversight can result in insufficient tokens for team and user claims, potentially leading to a first-come-first-serve scenario and a denial of service if totalSupply is less than dexAllocation. Additionally, the function does not check that the sum of ethToTeam and ethToDex equals fundraisingTarget, which can lead to a denial of service if ethToDex is less than fundraisingTarget. If the sum of ethToTeam and ethToDex is lower than fundraisingTarget, some funds will remain in the contract after the liquidity migration; at this point the creator can partially siphon them out by restarting the presale and withdrawing his deposits. Furthermore, the parameters ethToTeam and teamAllocation are not percentage-based and fixed within the contract, allowing creators to set them to zero. This allows creators to bypass the team revenue stream. The teamVestingDuration is also not fixed, which could be abused by creators to lock team's tokens being vested by either setting teamVestingDuration to an unreasonably large value, or to zero which will cause a Denial of Service in the claimTeamTokens function due to a division by zero.

## Recommendation
To address these issues, implement the same validation checks in the deployTokenWithCustomParams function as those in the addPresaleParams function. Ensure that the sum of dexAllocation, teamAllocation, and presaleAllocation equals totalSupply, and that ethToTeam plus ethToDex equals fundraisingTarget. Additionally, consider making ethToTeam and teamAllocation percentage-based and fixed within the contract to prevent creators from setting them to zero. Bound the teamVestingDuration to a reasonable value to prevent abuse.
