# [H] Attacker can leverage flashloans to steal rewards from vaults

## Summary
Severity: High
Chain: Smart contract
Component: StakeWise
Published: 2023-08-21
Source: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/14
Type: hats-finding

## Details
**Github username:** @milotruck
**Submission hash (on-chain):** 0x67eb9d6223a7aaec1b92a2c38d926f1a84febd850ffdbf70a53d157bd02e96b3
**Severity:** high

**Description:**
## Bug Description

In `KeeperRewards.sol`, the `isHarvestRequired()` function is used to determine if a vault needs to call `harvest()`:

[KeeperRewards.sol#L138-L146](https://github.com/stakewise/v3-core/blob/main/contracts/keeper/KeeperRewards.sol#L138-L146)

```solidity
  function isHarvestRequired(address vault) external view override returns (bool) {
    // vault is considered harvested in case it does not have any validators (nonce = 0)
    // or it is up to 1 rewards update behind
    uint256 nonce = rewards[vault].nonce;
    unchecked {
      // cannot overflow as nonce is uint64
      return nonce != 0 && nonce + 1 < rewardsNonce;
    }
  }
```

As seen from above, if a vault only has one pending update, `isHarvestRequired()` returns `false`, as vaults are allowed to be one update behind the latest one.

This becomes an issue as `isHarvestRequired()` is used to check if a vault needs to be harvested before a user makes a deposit:

[VaultEnterExit.sol#L151-L156](https://github.com/stakewise/v3-core/blob/main/contracts/vaults/modules/VaultEnterExit.sol#L151-L156)

```solidity
  function _deposit(
    address to,
    uint256 assets,
    address referrer
  ) internal virtual returns (uint256 shares) {
    _checkHarvested();
```


_Trimmed to 38 lines — full report: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/14_
