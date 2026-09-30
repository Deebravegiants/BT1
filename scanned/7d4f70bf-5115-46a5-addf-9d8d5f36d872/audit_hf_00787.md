# [C] C-05 | Attacker Can Drain All Funds from a Pool

## Summary
Severity: Critical
Contest weight: 0.2989
Dataset id: 2523
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _getMinReqAssetValue function in the RiskModule contract determines the minimum required asset value for a position to be considered healthy. This function is called by the isPositionHealthy function, which performs a health check after every action or series of actions taken by users to ensure their position remains healthy.

The issue arises because the _getMinReqAssetValue function relies on the length of the position's positionAssets array for the inner loop when calculating the required asset value for a position to be healthy. However, a position does not need to have any assets added to its positionAssets list in order to perform a borrow.

As a result, a user could perform a borrow with no funds, and the health check performed at the end would still pass. This occurs because _getMinReqAssetValue would return zero, given that the position's positionAssets is empty, despite the position having open debt from the borrow.

Consequently, a user could borrow all funds from a pool and transfer them to personal accounts, effectively draining the pool.

## Proof of Concept
https://github.com/GuardianAudits/sentiment-team-2/blob/POC_BYPASS_HEALTH_CHECK/test/guardian/pocs/pocBypassHealthCheck.t.sol

## Recommendation
Update the _getMinReqAssetValue function to revert if the resulting minReqAssetValue is zero. This function is only called when debt exceeds zero, so minReqAssetValue should almost always be greater than zero.

One exception is when a position's value falls to zero, causing insolvency. In such cases, this fix could block the liquidation of bad debt, so an admin function should be implemented to handle these scenarios.
