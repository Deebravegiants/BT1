# [M] Admin can break `_numberOfValidTokens`

## Summary
Severity: Medium
Contest weight: 0.5509
Dataset id: 1307
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `ProtocolGovernance._numberOfValidTokens` can be decreased by the admin in the `ProtocolGovernance.removeFromTokenWhitelist` function:

```solidity
    function removeFromTokenWhitelist(address addr) external {
        require(isAdmin(msg.sender), "ADM");
        _tokensAllowed[addr] = false;
        if (_tokenEverAdded[addr]) {
            // @audit admin can repeatedly call this function and sets _numberOfValidTokens to zero. because they don't flip _tokenEverAdded[addr] here
            --_numberOfValidTokens;
        }
    }
```

This function can be called repeatedly until the `_numberOfValidTokens` is zero.

## Recommendation
It seems that `_numberOfValidTokens` should only be decreased if the token was previously allowed:

```solidity
    function removeFromTokenWhitelist(address addr) external {
        require(isAdmin(msg.sender), "ADM");
        if (_tokensAllowed[addr]) {
            _tokensAllowed[addr] = false;
            --_numberOfValidTokens;
        }
    }
```

Can you confirm if this issue is valid or not? @MihanixA

Just realised this is a duplicate of another issue. Marking this as the primary issue

@0xleastwood Confirmed, it’s a bug.
