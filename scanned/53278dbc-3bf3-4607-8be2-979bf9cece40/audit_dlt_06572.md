# [M] Updating depthtreelimit is ineffective

## Summary
Severity: Medium
Chain: Smart contract
Component: Palmera
Published: 2024-06-24
Source: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/4
Type: hats-finding

## Details
**Github username:** @whoismxuse
**Twitter username:** __mxuse__
**Submission hash (on-chain):** 0xdc8f13fc9f47309f2617214ff27dce956df8a8b85156ef879c55cbaa5ab87f90
**Severity:** medium

**Description:**
## Description

Inside `PalmeraModule.sol` the following function allows for a new updated depth of the treelimit:
```javascript

    /// @dev Method to update Depth Tree Limit
    /// @param newLimit new Depth Tree Limit
    function updateDepthTreeLimit(uint256 newLimit)
        external
        IsRootSafe(_msgSender())
        requiresAuth
    {
        address caller = _msgSender();
        bytes32 org = getOrgHashBySafe(caller);
        uint256 rootSafe = getSafeIdBySafe(org, caller);
        if ((newLimit > maxDepthTreeLimit) || (newLimit <= depthTreeLimit[org]))
        {
            revert Errors.InvalidLimit();
        }
        emit Events.NewLimitLevel(
            org, rootSafe, caller, depthTreeLimit[org], newLimit
        );
->        depthTreeLimit[org] = newLimit;
    }
```
As you can see at the end of the function the `depthTreeLimit[org]` gets updated to the `newLimit`.

However due to the hardcoding of the `depthTreeLimit` inside several places of the contract, it will still remain 8:
```javascript
    function createRootSafe(address newRootSafe, string calldata name)
        external
        IsSafe(newRootSafe)
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/4_
