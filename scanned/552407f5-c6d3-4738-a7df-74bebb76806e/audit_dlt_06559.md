# [M] Safe owner/s can prevent being removed from organization by indefinitely increasing their child array

## Summary
Severity: Medium
Chain: Smart contract
Component: Palmera
Published: 2024-06-25
Source: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/51
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x8f22a5576088f17cc9d92e7f2f7708511899d90445a9ccaa2db87c91912da884
**Severity:** medium

**Description:**
**Description**\
Palmera module allow organizations to orchestrate different safes in hierarchy, where super safe can remove it's children. One problem here is that any arbitrary safe can become child of any  `superSafeId` by calling `addSafe`. This will increment 
`superSafeOrgSafe.child` array. There is no limit on how many child a super safe can have (the limit is only for depth), but a child may have an unlimited amount of siblings. Now lets see how a safe is removed from an organization:
```
 function removeSafe(uint256 safeId)
        public
        SafeRegistered(_msgSender())
        requiresAuth
    {
        address caller = _msgSender();
        bytes32 org = getOrgHashBySafe(caller);
        uint256 callerSafe = getSafeIdBySafe(org, caller);
        uint256 rootSafe = getRootSafe(safeId);
         ...
        /// Remove child from superSafe
        for (uint256 i; i < superSafe.child.length;) {
            if (superSafe.child[i] == safeId) {
                superSafe.child[i] = superSafe.child[superSafe.child.length - 1];
                superSafe.child.pop();
                break;
            }
            unchecked {
                ++i;
            }
        }
        // Handle child from removed safe
        for (uint256 i; i < _safe.child.length;) {
            // Add removed safe child to superSafe
            superSafe.child.push(_safe.child[i]);
            DataTypes.Safe storage childrenSafe = safes[org][_safe.child[i]];
            // Update children safe superSafe reference
            childrenSafe.superSafe = _safe.superSafe;
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/51_
