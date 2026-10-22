# [H] `utilization` for `_getInterestRate

## Summary
Severity: High
Contest weight: 0.3859
Dataset id: 19081
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The calculation for `utilization` in `_getInterestRate()` does not factor in the accrued interest. This leads to `_accrueInfo.interestPerSecond` being under-represented, and leading to incorrect interest rate calculation and potentially endangering conditions such as `utilization > maximumTargetUtilization` on line [124](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLCommon.sol#L124).

## Proof of Concept
The calculation for `utilization` in the `_getInterestRate()` function for `SGLCommon.sol` occurs on lines [61-64](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLCommon.sol#L61-L64) as a portion of the `fullAssetAmount` (which is also problematic) and the `_totalBorrow.elastic`. However, `_totalBorrow.elastic` is accrued by interest on line [99](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLCommon.sol#L99). This accrued amount is not factored into the calculation for `utilization`, which will be used to update the new interest rate, as purposed by the comment on line [111](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLCommon.sol#L111).

## Recommendation
Factor in the interest accrual into the `utilization` calculation:
    
    ...
            // Accrue interest
            extraAmount =
                (uint256(_totalBorrow.elastic) *
                    _accrueInfo.interestPerSecond *
                    elapsedTime) /
                1e18;
            _totalBorrow.elastic += uint128(extraAmount);
            
        +    uint256 fullAssetAmount = yieldBox.toAmount(    
        +        assetId,
        +        _totalAsset.elastic,
        +        false
        +    ) + _totalBorrow.elastic;
            //@audit utilization factors in accrual
        +    utilization = fullAssetAmount == 0
        +   ? 0
        +        : (uint256(_totalBorrow.elastic) * UTILIZATION_PRECISION) /
        +        fullAssetAmount;
    ...
