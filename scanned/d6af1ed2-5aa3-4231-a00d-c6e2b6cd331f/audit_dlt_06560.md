# [H] Malicious users can front-run host users safe management actions and add those safes as root for wrong org

## Summary
Severity: High
Chain: Smart contract
Component: Palmera
Published: 2024-06-25
Source: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/50
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x97ab4711dcc1016ca5ded1ad1bcdb25311cc3bc94f515794e86e5db4a87a3a1e
**Severity:** high

**Description:**
**Description**\
When creating a rootSafe for organization, we only check whether the calling address is a valid root safe and if provided address is a safe:
```   
 function createRootSafe(address newRootSafe, string calldata name)
        external
        IsSafe(newRootSafe)
        IsRootSafe(_msgSender())
        requiresAuth
        returns (uint256 safeId)
    {
        address caller = _msgSender();
        bytes32 org = getOrgHashBySafe(caller);
        uint256 newIndex = indexId;
        safeId = _createOrgOrRoot(name, caller, newRootSafe);
        // Setting level by default
        depthTreeLimit[org] = 8;

        emit Events.RootSafeCreated(org, newIndex, caller, newRootSafe, name);
    }
```
Note that a user can provide any `newRootSafe`, without guarantee if he is related to it. This is a big problem because once added in the system, `newRootSafe` cannot be added again from another organization. If this is weaponised, exploiter can DoS the composability of the palmera module by calling `createRootSafe` with address of other honest organization safes from his malicious organization. This will brick safe orchestration provided by palmera. This is so, because expoiter can prevent actors from calling `addSafe` and composing a tree. For example, malicious organisation can front-run `addSafe` by calling `createRootSafe` with address of the caller of `addSafe`. When honest party hit execution, it will revert on the following [line](https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/blob/dfd821e2fd7825c66c079c19be9460238f6e045a/src/PalmeraModule.sol#L357-L359):
```
        if (isSafeRegistered(caller)) {
            revert Errors.SafeAlreadyRegistered(caller);
        }
```

**Attack Scenario**\
1. Alice creates malicious organization `mal`
2. Bob creates root safe for his organisation.
3. Bob has 4 safes for his employees in work and want to add them 
hierarchically with his safe as root.

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/50_
