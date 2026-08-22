# [M] `Vault.mintWithPermit()` can be DOSed 

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-pooltogether
Published: 2023-07-14
Source: https://github.com/code-423n4/2023-07-pooltogether-findings/issues/384
Type: code-finding

## Details
# Lines of code

https://github.com/GenerationSoftware/pt-v5-vault/tree/b1deb5d494c25f885c34c83f014c8a855c5e2749/src/Vault.sol#L466-L469
https://github.com/GenerationSoftware/pt-v5-vault/tree/b1deb5d494c25f885c34c83f014c8a855c5e2749/src/Vault.sol#L971-L974
https://github.com/GenerationSoftware/pt-v5-vault/tree/b1deb5d494c25f885c34c83f014c8a855c5e2749/src/Vault.sol#L882-L887


# Vulnerability details

## Impact
`Vault.mintWithPermit()` uses a signature to approve the underlying asset. But the asset amount can be changed easily, so this method can be reverted and might be DoSed.

## Proof of Concept
`Vault.mintWithPermit()` gets the share amount as an input and calculates the asset amount from the share. And then approves the asset amount with `permit` method. 

```solidity
    uint256 _assets = _beforeMint(_shares, _receiver);

    _permit(IERC20Permit(asset()), msg.sender, address(this), _assets, _deadline, _v, _r, _s);
    _deposit(msg.sender, _receiver, _assets, _shares);
```

The signature is generated using the exact value of the expected asset amount calculated from the share amount, and the resulting asset amount depends on the exchange rate of current vault.

```solidity
  function _beforeMint(uint256 _shares, address _receiver) internal view returns (uint256) {
    if (_shares > maxMint(_receiver)) revert MintMoreThanMax(_receiver, _shares, maxMint(_receiver));
    return _convertToAssets(_shares, Math.Rounding.Up);
  }
```
```solidity
  function _convertToAssets(
    uint256 _shares,
    Math.Rounding _rounding
  ) internal view virtual override returns (uint256) {
    return _convertToAssets(_shares, _currentExchangeRate(), _rounding);
  }
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-pooltogether-findings/issues/384_
