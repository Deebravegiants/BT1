# [M] Killed Gauges Still Eligible For Rewards

## Summary
Severity: Medium
Contest weight: 0.3816
Dataset id: 13249
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function killGaugeTotally(address _gauge) external {
    require(msg.sender == emergencyCouncil, "not emergency council");
    require(isAlive[_gauge], "gauge already dead");
    isAlive[_gauge] = false;
    claimable[_gauge] = 0;
    address _pool = poolForGauge[_gauge];
    internal_bribes[_gauge] = address(0);
    external_bribes[_gauge] = address(0);
    gauges[_pool] = address(0);
    poolForGauge[_gauge] = address(0);
    isGauge[_gauge] = false;
    isAlive[_gauge] = false;
    claimable[_gauge] = 0;
    emit GaugeKilled(_gauge);
}
```

## Recommendation
Revise the above logic to properly remove a current gauge.
