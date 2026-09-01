# [M] Problems with `ensureNodeIsSafeModuleMember()`

## Summary
Severity: Medium
Chain: Smart contract
Component: SafeStaking-by-HOPR
Published: 2023-10-10
Source: https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/issues/23
Type: hats-finding

## Details
**Github username:** @0xfuje
**Submission hash (on-chain):** 0x0c43c16c3450cbcbfec8e6992239bf793f9c6912d9c4c8bb693b00ec0c35413a
**Severity:** medium

**Description:**
## Impact
Safes with multiple modules can't be registered or deregistered. A malicious module can pose as a `HoprNodeManagementModule`.

## Description
When registering or deregistering a `Safe` in `NodeSafeRegistry` - `ensureNodeIsSafeModuleMember()` is always called to make sure `HoprNodeManagementModule` is an enabled module of the `Safe`. The problem is that after `ensureNodeIsSafeModuleMember()` calls `getModulesPaginated()`, it will loop through all the `modules` and call `isHoprNodeManagementModule()` and `isNode()` functions on all of them. This will revert since other modules do not implement these functions. Calls revert in `solidity` if a non-existing function is called (if `fallback()` is not implemented).

`src/node-stake/NodeStakeRegistry.sol` - [`ensureNodeIsSafeModuleMember()`](https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/blob/master/packages/ethereum/contracts/src/node-stake/NodeSafeRegistry.sol#L266-L286)
```solidity
    /**
     * @dev Ensure that the node address is a member of
     * the enabled node management module of the safe
     * @param safeAddress Address of safe
     * @param nodeChainKeyAddress Address of node
     */
    function ensureNodeIsSafeModuleMember(address safeAddress, address nodeChainKeyAddress) internal view { 
        // nodeChainKeyAddress must be a member of the enabled node management module
        address nextModule;
        address[] memory modules;
        // there may be many modules, loop through them. Stop at the end point of the linked list
        while (nextModule != SENTINEL_MODULES) {
            // get modules for safe
            (modules, nextModule) = IAvatar(safeAddress).getModulesPaginated(SENTINEL_MODULES, pageSize); // @audit will revert
            for (uint256 i = 0; i < modules.length; i++) {
                if (
                        IHoprNodeManagementModule(modules[i]).isHoprNodeManagementModule()
                        && IHoprNodeManagementModule(modules[i]).isNode(nodeChainKeyAddress)
                ) {
                    return;
                }
            }
        }

        // if nodeChainKeyAddress is not a member of a valid HoprNodeManagementModule to the safe, revert
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/issues/23_
