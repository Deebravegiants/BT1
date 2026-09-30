# [M] Using a value of 0 for MIN_RATE_AT_TARGET in AdaptiveIRM causes interest rate to reset incorrectly

## Summary
Severity: Medium
Contest weight: 0.5576
Dataset id: 2742
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function updateInterestRateAtTarget(AdaptiveIRMStorage storage s, uint8 _vault, int256 _newInterestRateAtTarget)
    internal
{
    s.endRateAt[_vault] = _newInterestRateAtTarget;
    s.lastUpdate[_vault] = int256(block.timestamp);

    emit UpdateInterestRateAtTarget(_vault, _newInterestRateAtTarget);
}
```

When using 0 for MIN_RATE_AT_TARGET, in the event that the interest rate decrease to the minimum then s.endRateAt will be set to zero.

```solidity
int256 err = (utilization - targetUtilization).sDivWad(errNomFactor);

int256 startRateAtTarget = s.endRateAt[_vault];

int256 avgRateAtTarget;
int256 endRateAtTarget;

if (startRateAtTarget == 0) {
    avgRateAtTarget = INITIAL_RATE_AT_TARGET;
    endRateAtTarget = INITIAL_RATE_AT_TARGET;
```

The next iteration of the interest rate changes will see this 0 value and it will function as if the vault was never initialized. This will incorrectly set the interest rates to the initial rate rather than charging the 0% interest rate.

## Recommendation
MIN_RATE_AT_TARGET should always be a nonzero value
