# [M] Single signer can disable `HoprNodeManagementModule`

## Summary
Severity: Medium
Chain: Smart contract
Component: SafeStaking-by-HOPR
Published: 2023-10-11
Source: https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/issues/27
Type: hats-finding

## Details
**Github username:** @0xfuje
**Submission hash (on-chain):** 0xc42262e4f11eeed7e0277029f551a59963b2c77f6e693c6f05ec8b2ddde92b62
**Severity:** medium

**Description:**
## Impact
`HoprNodeManagementModule` is disabled from `Safe`, makes essential functionality of `SafeStaking` inaccessible

## Description
Threshold is set to one at `Safe`'s initialization, this means a single signer can disable `HoprNodeManagementModule`: making core functionality of  `SafeStaking by HOPR` unusable. Even if threshold is set to higher, multiple signers can collude to disable the node management `module`.

`src/node-stake/NodeStakeFactory.sol` - `clone()` - (threshold of one at initialization)
```solidity
        bytes memory safeInitializer = abi.encodeWithSignature(
            "setup(address[],uint256,address,bytes,address,address,uint256,address)",
            admins,
            1, // threshold
            address(0),
            hex"00",
            SafeSuiteLib.SAFE_CompatibilityFallbackHandler_ADDRESS,
            address(0),
            0,
            address(0)
        );
```
Note that while registering or de-registering a node in `NodeSafeRegitry.sol` `ensureNodeIsSafeModuleMember()` is always called to make sure the module is registered, however after a node is registered (via `registerSafeByNode()`) the `HoprNodeManagementModule` can simply be disabled in `Safe` via `disableModule()`. The registry will still treat it as a registered node-safe combination and return `true` on calls made to `isNodeSafeRegistered()`.

`vendor/solidity/safe-contracts-1.4.1/contracts/base/ModuleManager.sol` - [`disableModule()`](https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/blob/master/vendor/solidity/safe-contracts-1.4.1/contracts/base/ModuleManager.sol#L63-L70)
```solidity
    function disableModule(address prevModule, address module) public authorized {
        // Validate module address and check that it corresponds to module index.
        require(module != address(0) && module != SENTINEL_MODULES, "GS101");
        require(modules[prevModule] == module, "GS103");
        modules[prevModule] = modules[module];
        modules[module] = address(0);
        emit DisabledModule(module);
    }
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/issues/27_
