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

This could lead to incorrect signature verification in `permit()` if the upgradeable contract's version is upgraded, but the hardcoded version in `_computeDomainSeparator()` is unchanged.

## Attack Scenario

Consider the following scenario:
- An `EthErc20Vault` is initially deployed with `version()` returning `1`.
- After some time, a some changes are made to the `EthErc20Vault` contract:
  - To differentiate between versions, `version()` returns `2` in the new implementation contracct.
- The vault's admin upgrades the vault's implementation contract to the new contract:
  - Now, when the vault's `version()` function is called, it returns `2`.
- However, the version in `_computeDomainSeparator()` remains unchanged.
- Therefore, the domain seperator used for signature verification in `permit()` is incorrect due to the outdated version.

## Impact

If an `EthErc20Vault` is upgraded to a newer version, the `permit()` function will still verify signatures with `version = 1`, making its signature verification incorrect.

Therefore, after the upgrade, contracts/frontends that rely on the `version()` function will end up generating different signatures, causing `permit()` to revert when called.

Furthermore, signatures that were signed for the vault's previous version can still be used. This is problematic as users expect their older signatures to become invalid due to the change in the vault's version and functionality.

## Recommended Mitigation

Consider updating the version in `_computeDomainSeperator()` when `version()` changes. This can be achieved by doing the following:

1. In `ERC20Upgradeable.sol`, add a new state variable named `version`: 

```solidity
string public override version;
```

2. In `_computeDomainSeparator()`, use `version` instead of a hardcoded value: 

[ERC20Upgradeable.sol#L144-L157](https://github.com/stakewise/v3-core/blob/main/contracts/base/ERC20Upgradeable.sol#L144-L157)

```diff
  function _computeDomainSeparator() private view returns (bytes32) {
    return
      keccak256(
        abi.encode(
          keccak256(
            'EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)'
          ),
          keccak256(bytes(name)),
-         keccak256('1'),
+         keccak256(bytes(version)),
          block.chainid,
          address(this)
        )
      );
  }
```

3. Modify `__ERC20Upgradeable_init()` to take in a `_version` parameter used to initialize `version`:

[ERC20Upgradeable.sol#L170-L180](https://github.com/stakewise/v3-core/blob/main/contracts/base/ERC20Upgradeable.sol#L170-L180)

```diff
  function __ERC20Upgradeable_init(
    string memory _name,
-   string memory _symbol
+   string memory _symbol,
+   string memory _version
  ) internal onlyInitializing {
    // initialize ERC20
    name = _name;
    symbol = _symbol;
+   version = _version;

    // initialize EIP-2612
    _initialDomainSeparator = _computeDomainSeparator();
  }
```

4. Modify `__VaultToken_init()` to take in a `version` parameter that is passed to `__ERC20Upgradeable_init()`:

[VaultToken.sol#L65-L70](https://github.com/stakewise/v3-core/blob/main/contracts/vaults/modules/VaultToken.sol#L65-L70)

```diff
- function __VaultToken_init(string memory _name, string memory _symbol) internal onlyInitializing {
+ function __VaultToken_init(string memory _name, string memory _symbol, string memory version) internal onlyInitializing {
    if (bytes(_name).length > 30 || bytes(_symbol).length > 10) revert Errors.InvalidTokenMeta();

    // initialize ERC20Permit
-   __ERC20Upgradeable_init(_name, _symbol);
+   __ERC20Upgradeable_init(_name, _symbol, version);
  }
```

5. In `__EthErc20Vault_init()`, pass `version()` into `__VaultToken_init()`:

[EthErc20Vault.sol#L184](https://github.com/stakewise/v3-core/blob/main/contracts/vaults/ethereum/EthErc20Vault.sol#L184)

```diff
-   __VaultToken_init(params.name, params.symbol);
+   __VaultToken_init(params.name, params.symbol, version());
```

This ensures that `_computeDomainSeparator()` will always use the same version as the `version()` function as long as `__EthErc20Vault_init()` is called after every upgrade.
