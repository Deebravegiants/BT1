# [M] Version in `_computeDomainSeparator()` isn't updated when contracts inheriting `ERC20Upgradeable.sol` are upgraded

## Summary
Severity: Medium
Chain: Smart contract
Component: StakeWise
Published: 2023-08-26
Source: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/116
Type: hats-finding

## Details
**Github username:** @milotruck
**Submission hash (on-chain):** 0xc04addd385d6126e577c70f6cbcabf47744c9284a8b23a6f6e21b837f8e4276e
**Severity:** medium

**Description:**
## Bug Description

In `ERC20Upgradeable.sol`, the `_computeDomainSeparator()` function is used to build the domain seperator that is used for signature verification in [`permit()`](https://github.com/stakewise/v3-core/blob/main/contracts/base/ERC20Upgradeable.sol#L97-L133):

[ERC20Upgradeable.sol#L144-L157](https://github.com/stakewise/v3-core/blob/main/contracts/base/ERC20Upgradeable.sol#L144-L157)

```solidity
  function _computeDomainSeparator() private view returns (bytes32) {
    return
      keccak256(
        abi.encode(
          keccak256(
            'EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)'
          ),
          keccak256(bytes(name)),
          keccak256('1'), // @audit hardcoded version here
          block.chainid,
          address(this)
        )
      );
  }
```

As seen from above, the version is hardcoded to `1`. This is problematic as `ERC20Upgradeable` is meant to be inherited by upgradeable contracts that have changing versions. An example of this would be `EthErc20Vault.sol`, which has a `version()` function:

[EthErc20Vault.sol#L137-L139](https://github.com/stakewise/v3-core/blob/main/contracts/vaults/ethereum/EthErc20Vault.sol#L137-L139)

```solidity
  function version() public pure virtual override(IVaultVersion, VaultVersion) returns (uint8) {
    return 1;
  }
```


_Trimmed to 38 lines — full report: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/116_
