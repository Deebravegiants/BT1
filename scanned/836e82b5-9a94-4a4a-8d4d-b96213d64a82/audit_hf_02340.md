# [H] Revisited Logic on allocateSeigniorage()/getDollarExpansionRate()

## Summary
Severity: High
Contest weight: 0.5258
Dataset id: 12713
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function allocateSeigniorage() external onlyOneBlock checkCondition checkEpoch checkOperator {
    _updateDollarPrice();
    previousEpochDollarPrice = getDollarPrice();
    uint256 dollarSupply = getDollarCirculatingSupply().sub(seigniorageSaved);
    if (epoch < bootstrapEpochs)
        // 21 first epochs with
```

## Recommendation
No data
