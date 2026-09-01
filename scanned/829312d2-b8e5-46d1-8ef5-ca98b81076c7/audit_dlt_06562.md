# [H] Incorrect access control on removeSafe()

## Summary
Severity: High
Chain: Smart contract
Component: Palmera
Published: 2024-06-24
Source: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/40
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x23a6cabda11ab9239e0276fc86820ace1efb5cb48b94811ea20f35345fe1e528
**Severity:** high

**Description:**
**Description**\

`removeSafe()` is used to remove safe and reasign all child to the superSafe. This is implemented as:

```solidity
    function removeSafe(uint256 safeId)
        public
        SafeRegistered(_msgSender())
        requiresAuth
    {

    . . . some code . .. 
   }
```

The shared Palmera documentation specifically states:

```
 Remove a Safe
 Function: removeSafe()
 Description: Removes a safe. This must be called by the root safe.
```

The documentation states, `removeSafe()` MUST be called by root safe, however the current implementation does not implement it and unsafe from intended protocol design for `removeSafe()`. This would not ensure, the strict access control on `removeSafe()` as intended by Palmera protocol as the access to such critical function is given in wrong hands and no where it mentions to allow `SafeRegistered()` to access `removeSafe()`. 

**Recommendation**\
only allow root safe to access the `removeSafe()` function as intended in documentation.

For example: Consider below changes:

```diff
    function removeSafe(uint256 safeId)
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/40_
