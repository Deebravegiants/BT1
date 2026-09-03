# [M] If `InverterTransparentUpgradeableProxy_v1` won't not be affected by shut down implementation

## Summary
Severity: Medium
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-07
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/55
Type: hats-finding

## Details
**Github username:** @NicolaMirchev
**Twitter username:** nmirchev8
**Submission hash (on-chain):** 0xf720b02ef286358ba83c3a0a7feb911513866cdc5880152be81792cfebf4357a
**Severity:** medium

**Description:**
**Description**\

The protocol is using beacon proxy pattern to efficiently deploy new modules. Here is how the deployment of a new module is happening using a proxy, which is forwarding to a beacon implementation.
```
        if (workflowConfig.independentUpdates) {
            // Use an InverterTransparentUpgradeableProxy as a proxy
            proxy = address(
                new InverterTransparentUpgradeableProxy_v1(
                    beacon, workflowConfig.independentUpdateAdmin, bytes("")
                )
            );
        }
        // If not then
        else {
            // Instead use the Beacon Structure Proxy
            proxy = address(new InverterBeaconProxy_v1(beacon));
        }
```
`beacon` is always verified module implementation.
We notice that there are also two proxy implemenatations. 
- `InverterBeaconProxy_v1`
- `InverterTransparentUpgradeableProxy_v1` is used if owner of the module want to have the freedom to decide whether to update to the newest implementation version.

But there is also another small difference between the two proxies, which may lead to further problems and that is the way each protocol is reading current implementation contract:
`InverterBeaconProxy_v1`
```
    function _implementation() internal view override returns (address) {
        return _beacon.implementation();
    }
```

`InverterTransparentUpgradeableProxy_v1`:

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/55_
