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

[VaultImmutables.sol#L41-L43](https://github.com/stakewise/v3-core/blob/main/contracts/vaults/modules/VaultImmutables.sol#L41-L43)

```solidity
  function _checkHarvested() internal view {
    if (IKeeperRewards(_keeper).isHarvestRequired(address(this))) revert Errors.NotHarvested();
  }
```

As users are allowed to deposit when the latest update has not been harvested, an attacker can abuse flashloans to deposit a huge amount of assets and steal the profits from the latest update.

## Attack Scenario

Consider the following scenario:
- [`updateRewards()`](https://github.com/stakewise/v3-core/blob/main/contracts/keeper/KeeperRewards.sol#L82-L125) is called to update rewards for all vaults.
- An attacker sees that a certain vault has a made a huge profit.
- To steal most of the profit from that vault, he does the following:
  - Borrow 1000 ether using a flashloan.
  - Call [`deposit()`](https://github.com/stakewise/v3-core/blob/main/contracts/vaults/modules/VaultEthStaking.sol#L33-L39) to deposit 1000 ether as assets into the vault.
  - Call [`updateState()`](https://github.com/stakewise/v3-core/blob/main/contracts/vaults/modules/VaultState.sol#L86-L98), which adds profits from the latest update to the vault's assets.
  - Call [`redeem()`](https://github.com/stakewise/v3-core/blob/main/contracts/vaults/modules/VaultEnterExit.sol#L29-L54) to withdraw all his shares for ETH.
  - Repay his flashloan.
- Due to the attacker's large deposit, he held most of the shares in the vault when `updateState()` was called.
- Therefore, after `updateState()` is called, most of the vault's profits from the latest rewards update is accrued to his shares, allowing him to withdraw more than 1000 ether when calling `redeem()`.

In the scenario above, the attacker has managed to gain most of the vault's profits at no risk, which is a theft of yield from other stakers.

## Impact

As users can make deposits while the vault is one rewards update behind, an attacker can leverage flashloans to steal most of the yield from the latest rewards update. This can be done without any risk as attackers can call `redeem()` in the same transaction as `deposit()`.

## Recommended Mitigation

Consider only allowing deposits and other functions to be called when all pending updates has been harvested. This can be achieved by making `isHarvestRequired()` return `true` when the vault is 1 rewards update behind:

[KeeperRewards.sol#L138-L146](https://github.com/stakewise/v3-core/blob/main/contracts/keeper/KeeperRewards.sol#L138-L146)

```diff
  function isHarvestRequired(address vault) external view override returns (bool) {
    // vault is considered harvested in case it does not have any validators (nonce = 0)
    // or it is up to 1 rewards update behind
    uint256 nonce = rewards[vault].nonce;
    unchecked {
      // cannot overflow as nonce is uint64
-     return nonce != 0 && nonce + 1 < rewardsNonce;
+     return nonce != 0 && nonce < rewardsNonce;
    }
  }
```
