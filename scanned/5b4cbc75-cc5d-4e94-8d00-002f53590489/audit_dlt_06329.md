# [M] CatalystVault fee administrators can steal all value from unsuspecting users via front-running

## Summary
Severity: Medium
Chain: Smart contract
Component: Catalyst-Exchange
Published: 2024-01-24
Source: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/13
Type: hats-finding

## Details
**Github username:** @0xfuje
**Twitter username:** 0xfuje
**Submission hash (on-chain):** 0x82ca8edd6f7b46cf2d7d9d7052d98aa2d7e177461cbdd0e149bb411b928a6efe
**Severity:** medium

**Description:**
## Impact 
User loses total value sent to the vault (meant for swap or cross-chain send)

## Description
Whenever a vault is initialized via `CatalystFactory.deployVault()`, the owner of the catalyst factory is set as the fee administrator of the particular deployed vault. The fee administrator can be changed to any address by the factory owner. Regardless of the current role owner, the fee administrator can abuse their privileges and steal all possible value from users while on the surface the vault fee remains normal.

`catalyst/evm/src/CatalystVaultCommon.sol` - `setFeeAdministrator()`
```solidity
function setFeeAdministrator(address administrator) public override onlyFactoryOwner {
	_setFeeAdministrator(administrator);
}
```

One of the weaknesses that allows this vulnerability is the weak upper bound of `_setVaultFee()` as it can be set to 100%. It should be a safer value that still allows to set a relatively high fee, e.g. 20%. 

`catalyst/evm/src/CatalystVaultCommon.sol` - [`_setVaultFee()`](https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/blob/27b4d0a2bca177aff00def8cd745623bfbf7cb6b/evm/src/CatalystVaultCommon.sol#L347-L351)
```solidity
function  _setVaultFee(uint256 fee) internal { // @audit low - vault fee of 100% is dangerous
	require(fee <= 1e18); // dev: VaultFee is maximum 100%.
	_vaultFee = fee;
	emit  SetVaultFee(fee);
}
```

Another weakness to mention is that a lot of users tend to not set `minOut` values, and swapping withing a vault via `localSwap()` and sending asset via `sendAsset()` and other vault actions does not check that the `minOut` value is actually zero.

Note that if we assume the factory owner never turns malicious, and fee admin role has been transferred, the new fee admin can still grief users to lose all of their value used via the vault.

`catalyst/evm/src/CatalystVaultVolatile.sol` - [`localSwap()`](https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/blob/27b4d0a2bca177aff00def8cd745623bfbf7cb6b/evm/src/CatalystVaultVolatile.sol#L565-L592)
```solidity
    function localSwap(
        address fromAsset,
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/13_
