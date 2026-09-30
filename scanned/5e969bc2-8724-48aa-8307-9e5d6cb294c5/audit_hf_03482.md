# [M] Vault does not conform to ERC4626

## Summary
Severity: Medium
Contest weight: 0.5769
Dataset id: 19028
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability concerns a PoolTogether V5 Vault that implements the ERC4626 tokenized vault interface but provides non‑conforming implementations of the maxDeposit and maxMint view functions. According to the ERC4626 specification, maxDeposit(address) must return the exact maximum amount of assets that can be deposited for a given receiver without causing a revert, and this value must never exceed the true capacity of the underlying vault. Likewise, maxMint(address) must return the maximum number of shares that can be minted for a receiver under the same constraints. In the examined contract, both functions simply check an internal collateralisation flag and, when true, return type(uint96).max – a constant that represents the largest value that fits in a 96‑bit unsigned integer – regardless of the actual limits of the external yield vault that the PoolTogether Vault forwards deposits to. The root cause is that the implementation ignores the capacity reported by the connected ERC4626‑compliant yield vault (_yieldVault) and therefore over‑estimates the amount that can be safely deposited or minted. An external caller that queries maxDeposit or maxMint will be told that an arbitrarily large amount can be supplied, and may attempt to deposit that amount. When the underlying yield vault cannot accept the requested assets because its own maxDeposit or maxMint is lower, the transaction reverts. From a user’s perspective the UI may display a huge “maximum deposit” number, the user approves a large amount, but the transaction fails and no assets are transferred, leading to confusion and a perception that the protocol is broken. This bug can also break integrations that rely on the ERC4626 interface to compute safe deposit limits, potentially causing downstream contracts to lock funds or to abort operations. The issue was discovered during a Code4rena audit by comparing the contract’s behaviour against the ERC4626 specification. It is hard to notice because the functions return a plausible large number and only manifest as a failure when a deposit is actually attempted. The vulnerability belongs to the class of ERC4626 compliance errors where maxDeposit/maxMint do not reflect the true capacity of the underlying asset manager. To remediate, the contract should query the external vault’s maxDeposit and maxMint for the given receiver, then return the lesser of that value and type(uint96).max, as shown in the recommended code changes. This ensures that the reported limits are accurate, prevents unexpected reverts, and restores compatibility with any ERC4626‑aware tooling or contracts.

## Proof of Concept
The ERC4626 specification states that `maxDeposit` MUST return the maximum amount of assets deposit would allow to be deposited for receiver and not cause a revert, which MUST NOT be higher than the actual maximum that would be accepted.

Similarly, `maxMint` MUST return the maximum amount of shares mint would allow to be deposited to receiver and not cause a revert, which MUST NOT be higher than the actual maximum that would be accepted.

The PoolTogether V5 Vault connects to an external ERC4626-compliant Vault (`_yieldVault`) and deposits incoming assets in it. This means, that `maxDeposit` and `maxMint` of the PoolTogether Vault must be constrained by the `maxDeposit` and `maxMint` of the external Vault.

## Recommendation
Replace the implementation of `maxDeposit`:

```solidity
function maxDeposit(address) public view virtual override returns (uint256) {
    return _isVaultCollateralized() ? type(uint96).max : 0;
  }
```

with:

```solidity
function maxDeposit(address receiver) public view virtual override returns (uint256) {
    if (!_isVaultCollateralized()) return 0;

    uint256 yvMaxDeposit = _yieldVault.maxDeposit(receiver);
    return yvMaxDeposit < type(uint96).max ? yvMaxDeposit : type(uint96).max;
  }
```

Analogously, change the implementation of `maxMint` from:

```solidity
function maxMint(address) public view virtual override returns (uint256) {
    return _isVaultCollateralized() ? type(uint96).max : 0;
  }
```

to:

```solidity
function maxMint(address receiver) public view virtual override returns (uint256) {
    if(!_isVaultCollateralized()) return 0;

    uint256 yvMaxMint = _yieldVault.maxDeposit(receiver);
    return yvMaxMint < type(uint96).max ? yvMaxMint : type(uint96).max;
  }
```
