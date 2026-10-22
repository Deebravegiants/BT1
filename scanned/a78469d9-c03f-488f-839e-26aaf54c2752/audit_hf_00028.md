# [M] RSKE-3 | Incorrect X and Y in positionMaintenanceMargin

## Summary
Severity: Medium
Contest weight: 0.0725
Dataset id: 104
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When computing the margin positionMaintenanceMargin function, the X and Y values are in an incorrect order. According to [documentation](https://ivx-1.gitbook.io/ivx-1/financial-model/maintenance-margin): Maintenance Margin=a * Max(b * X+c * Y ; d * Y+e * X)

## Recommendation
function positionMaintenanceMargin(uint256 X, uint256 Y, address _asset) public view returns (uint256 margin) { AssetAttributes memory asset = assetAttributes[_asset]; margin = asset.marginFactors.marginFactorA.mulDivUp( Math.max( (asset.marginFactors.marginFactorB * X) + (asset.marginFactors.marginFactorC * Y), - (asset.marginFactors.marginFactorD * X) + (asset.marginFactors.marginFactorE * Y) + (asset.marginFactors.marginFactorD * Y) + (asset.marginFactors.marginFactorE * X) ), 1e36 ); }
