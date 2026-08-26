# [M] Vault does not conform to ERC4626

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-pooltogether
Published: 2023-07-12
Source: https://github.com/code-423n4/2023-07-pooltogether-findings/issues/129
Type: code-finding

## Details
# Lines of code

https://github.com/GenerationSoftware/pt-v5-vault/blob/b1deb5d494c25f885c34c83f014c8a855c5e2749/src/Vault.sol#L375-L377
https://github.com/GenerationSoftware/pt-v5-vault/blob/b1deb5d494c25f885c34c83f014c8a855c5e2749/src/Vault.sol#L383-L385


# Vulnerability details

## Impact
`Vault` does not conform to ERC4626 which may break external integrations

## Proof of Concept
The [ERC4626 specification](https://eips.ethereum.org/EIPS/eip-4626) states that `maxDeposit` *MUST return the maximum amount of assets `deposit` would allow to be deposited for receiver and not cause a revert, which MUST NOT be higher than the actual maximum that would be accepted*. 

Similarly, `maxMint` *MUST return the maximum amount of shares mint would allow to be deposited to receiver and not cause a revert, which MUST NOT be higher than the actual maximum that would be accepted.*

The PoolTogether V5 `Vault` connects to an external ERC4626-compliant Vault (`_yieldVault`) and deposits incoming assets in it. This means that `maxDeposit` and `maxMint` of the PoolTogether Vault must be constrained by the `maxDeposit` and `maxMint` of the external Vault.

## Tools Used
Manual review, [ERC-4626: Tokenized Vaults](https://eips.ethereum.org/EIPS/eip-4626)

## Recommended Mitigation Steps
Replace the implementation of `maxDeposit`
```
  function maxDeposit(address) public view virtual override returns (uint256) {
    return _isVaultCollateralized() ? type(uint96).max : 0;
  }
``` 
with:
```
  function maxDeposit(address receiver) public view virtual override returns (uint256) {
    if (!_isVaultCollateralized()) return 0;

    uint256 yvMaxDeposit = _yieldVault.maxDeposit(receiver);
    return yvMaxDeposit < type(uint96).max ? yvMaxDeposit : type(uint96).max;
  }
```


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-pooltogether-findings/issues/129_
