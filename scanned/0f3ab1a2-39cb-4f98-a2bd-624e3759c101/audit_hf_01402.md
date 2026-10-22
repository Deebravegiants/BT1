# [M] Invariants are not checked after calling calculateDistributeExcessIdleShareProceedsNetLongEdge- CaseSafe

## Summary
Severity: Medium
Contest weight: 0.1443
Dataset id: 7181
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
calculateDistributeExcessIdleShareProceedsNetLongEdgeCaseSafe returns:
z_proceed = z_og - ((z_og / P_og) * (sLP / (sLP + sW)) * PV0 - z_flat)
or in other words:
z_og - (1 / P_og) * (sLP / (sLP + sW)) * PV0 - z_flat
1. This scaling is independent of the number of iterations performed in the Newton approximation loop. This is not really an issue just an observation that one the calculation ones picks this specific value only depending on the original point.
2. After one finds z we still need to check that uint256(_params.netCurveTrade) <= maxBondAmount is false on the updated curve C(z, P, y), otherwise the assumption where z + z_curve - z_min = (P_og / z_og) * z would be wrong which would break: PV0 / (sLP + sW) = PV1 / sLP
3. z_proceed is not compared to the idle share reserves to make sure it cannot be greater than that value, we need to check: z_proceed ≤ I

## Recommendation
2. After updating the point to the new point (z, P, y) by the scaling factor: λ = 1 / P_og * (sLP / (sLP + sW)) * PV0 - z_flat Make sure that uint256(_params.netCurveTrade) <= maxBondAmount is false.
3. Check that z_proceed ≤ I.
DELV:
2. has been applied in PR 800, which had an error that was fixed in PR 827.
3. The above PRs along with PR 771 below will guarantee 3.
