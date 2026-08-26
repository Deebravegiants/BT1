# [M] `GaugeFactoryUpgradeable.setDistribution()` would revert due to incorrect access control

## Summary
Severity: Medium
Chain: Smart contract
Component: Fenix-Finance
Published: 2024-02-27
Source: https://github.com/hats-finance/Fenix-Finance-0x83dbe5aa378f3ce160ed084daf85f621289fb92f/issues/23
Type: hats-finding

## Details
**Github username:** @0xRizwan
**Twitter username:** 0xRizwann
**Submission hash (on-chain):** 0x92d750511244e578f717387ba7dc6ca37b88548ac3fb7c0056bf68d50d6165ac
**Severity:** medium

**Description:**
**Description**\

`GaugeFactoryUpgradeable.setDistribution()` is used to set the `DISTRIBUTION` address.

```solidity

    function setDistribution(address _gauge, address _newDistribution) external onlyOwner {
        _checkAddressZero(_newDistribution);
        IGauge(_gauge).setDistribution(_newDistribution);
    }
```

This function calls setDistribution from guage contract which looks as below per implementation,

`GaugeUpgradeable.setDistribution()`

```solidity
    function setDistribution(address _distribution) external onlyOwner {
        require(_distribution != address(0), "zero addr");
        require(_distribution != DISTRIBUTION, "same addr");
        DISTRIBUTION = _distribution;
    }
```

This function can only be accessed by `onlyOwner` and this modifier implementation is shown as below,


```solidity

    modifier onlyOwner() {
        require(msg.sender == IGaugeFactory(gaugeFactory).gaugeOwner());
        _;
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Fenix-Finance-0x83dbe5aa378f3ce160ed084daf85f621289fb92f/issues/23_
