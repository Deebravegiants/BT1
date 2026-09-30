# [M] Vault does not fully conform to `EIP4626`

## Summary
Severity: Medium
Reporter: berndartmueller
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# Vault does not fully conform to `EIP4626`

## Summary

The `VaultBase` contract does not fully conform to the `EIP4626` standard.

## Vulnerability Detail

The `VaultBase` contract implements the `EIP4626` standard ([EIP-4626: Tokenized Vault Standard](https://eips.ethereum.org/EIPS/eip-4626)).

However, according to `EIP4626`, the below-mentioned functions do not fully adhere to the specs.

**ERC4626Base.maxWithdraw** _(Found in @solidstate/contracts/token/ERC4626/base/ERC4626Base.sol)_

```solidity
function maxWithdraw(address owner)
    external
    view
    returns (uint256 maxAssets)
{
    maxAssets = _maxWithdraw(owner); // @audit-info `_maxWithdraw` is the default implementation in @solidstate's ERC4626BaseInternal.sol and not overwritten by Knox
}
```

1. MUST factor in global and user-specific limits, if deposits are entirely disabled (even temporarily) it MUST return 0. The vault has a withdrawal lock which is active after the auction has started and deactivated when the auction is processed. Therefore, this withdrawal lock state should be reflected in the `maxWithdraw` function to be compliant.

**ERC4626Base.maxRedeem** _(Found in @solidstate/contracts/token/ERC4626/base/ERC4626Base.sol)_

```solidity
function maxRedeem(address owner)
    external
    view
    returns (uint256 maxShares)
{
    maxShares = _maxRedeem(owner); // @audit-info `_maxRedeem` is the default implementation in @solidstate's ERC4626BaseInternal.sol and not overwritten by Knox
}
```

1. MUST factor in global and user-specific limits, if deposits are entirely disabled (even temporarily) it MUST return 0. The vault has a withdrawal lock which is active after the auction has started and deactivated when the auction is processed. Therefore, to be compliant, this withdrawal lock state should be reflected in the `maxRedeem` function.

## Impact

Not adhering to the `EIP4626` standard could lead to integration issues with other protocols.

## Code Snippet

See above.

## Tool Used

Manual review

## Recommendation

Consider implementing the `EIP4626` standard as close to the specs as possible.
