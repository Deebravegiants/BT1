# [H] _computeClosingFactor function will return incorrect liquidated amount

## Summary
Severity: High
Contest weight: 0.3772
Dataset id: 22564
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
_computeClosingFactor is used to calculate the required borrow amount that should be liquidated to make the user's position solvent. However, this function uses collateralizationRate (defaulting to 75%) to calculate the liquidated amount, while the threshold to be liquidatable is liquidationCollateralizationRate (defaulting to 80%). Therefore, it will return incorrect liquidated amount. In _computeClosingFactor of Market contract: A user will be able to be liquidated if their ratio between borrow and collateral value exceeds liquidationCollateralizationRate (see _isSolvent() function). However, _computeClosingFactor uses collateralizationRate (defaulting to 75%) to calculate the denominator for the needed liquidate amount, while the numerator is calculated by using liquidationCollateralizationRate (80% in default). These variables were initialized in _initCoreStorage(). In the above calculation of _computeClosingFactor function, in default: _liquidationMultiplier = 12%, numerator = borrowPart - liquidationStartsAt = borrowAmount - 80% * collateralToAssetAmount => x will be: numerator / (1 - 75% * 112%) = numerator / 16% However, during a partial liquidation of BigBang or Singularity, the actual collateral bonus is liquidationBonusAmount, defaulting to 10%. (code snippet). Therefore, the minimum liquidated amount required to make user solvent (unable to be liquidated again) is: numerator / (1 - 80% * 110%) = numerator / 12%. As result, computeClosingFactor() function will return a lower liquidated amount than needed to make user solvent, even when that function attempts to over-liquidate with _liquidationMultiplier > liquidationBonusAmount. This issue will result in the user still being liquidatable after a partial liquidation because it liquidates a lower amount than needed. Therefore, the user will never be solvent again after they are undercollateralized until their position is fully liquidated. This may lead to the user being liquidated more than expected, or experiencing a loss of funds in attempting to recover their position.

## Recommendation
Use liquidationCollateralizationRate instead of collateralizationRate to calculate the denominator in _computeClosingFactor
