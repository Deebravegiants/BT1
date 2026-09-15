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
```
    function getImplementation() internal view returns (address) {
        return StorageSlot.getAddressSlot(IMPLEMENTATION_SLOT).value;
    }
```
So `InverterBeaconProxy_v1` is dynamically reading the implementation address from provided `beacon` on construction. On the other hand `InverterTransparentUpgradeableProxy_v1` is setting the implementation on `beacon.getImplementationAddress()` during construction. 
The problem is that if a Governance trigger a shutdown of a beacon, this would only affect modules, which are using `InverterBeaconProxy_v1`.
**Attack Scenario**\
Imagine the following scenario:

- Lets say current version is 1.
- Bob deploys a payment module using `InverterTransparentUpgradeableProxy_v1`, because current version would be satisfactory for his future needs.  
- There is an issue found with that implementation and protocol shut it down with `initiateBeaconShutdown` and publicly announce why they have shutdown the version (share the expoit)
- Bob is a victim, because he cannot "shutdown" the implementation by calling `upgradeToNewestVersion`, because instead of changing the current implementation to address(0) (which is being shutdown), the tx will revert because of the following OZ code:
```
    function _setImplementation(address newImplementation) private {
        if (newImplementation.code.length == 0) {
            revert ERC1967InvalidImplementation(newImplementation);
        }
        StorageSlot.getAddressSlot(IMPLEMENTATION_SLOT).value = newImplementation;
    }
```

**Attachments**

1. **Proof of Concept (PoC) File**
Will provide in comments if needed.
2. **Revised Code File (Optional)**
- Inside beacon implement some kind of a mapping `versionIsShutdown(version => true)` to track whether a version is shutdown.
- Inside `InverterTransparentUpgradeableProxy_v1` override `_implementation` to dynamically get it from the proxy, but also using the new mapping to fetch the status of the version. (If it has been shut down, return `address(0)`)
