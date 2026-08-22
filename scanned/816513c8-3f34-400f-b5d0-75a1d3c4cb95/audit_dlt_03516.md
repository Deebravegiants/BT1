# [M] Admin can break `_numberOfValidTokens`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-12-mellow
Published: 2021-12-08
Source: https://github.com/code-423n4/2021-12-mellow-findings/issues/49
Type: code-finding

## Details
# Handle

cmichel


# Vulnerability details

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

## Impact
The `_numberOfValidTokens` is wrong and with it the `tokenWhitelist()`.

## Recommended Mitigation Steps
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
