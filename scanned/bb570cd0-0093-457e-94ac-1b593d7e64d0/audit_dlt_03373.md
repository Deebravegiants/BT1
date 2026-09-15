# [H] Vaults are in liquidation forever instead of just for auction length

## Summary
Severity: High
Chain: Smart contract
Component: 2021-05-yield
Published: 2021-06-01
Source: https://github.com/code-423n4/2021-05-yield-findings/issues/31
Type: code-finding

## Details
# Handle

cmichel


# Vulnerability details

The witch can `Witch.grab` vaults and the `vaultOwners[vaultId]` field is set to the original owner.
The original vault owner is only restored if all debt (`balances_.art`) is repaid by the liquidation engine.

```solidity
if (balances_.art - art == 0) { // If there is no debt left, return the vault with the collateral to the owner
    cauldron.give(vaultId, vaultOwners[vaultId]);
    delete vaultOwners[vaultId];
}
```

Note that there's no check in `settle` verifying that the auction time (from `grab`) is not over yet, as well as no check that the vault is actually still undercollateralized.

## Impact
Once a vault is grabbed by the witch it'll be susceptible to liquidations forever. All debt has to be repaid to get the vault out of a liquidation state again.
An example would be that a vault becomes undercollateralized, the witch grabs it, the network is congested and nobody is able to liquidate it, the auction time is over, the collateral value has increased in the meantime and the vault is not undercollateralized anymore.
Liquidators can still liquidate this vault whenever they want which doesn't seem fair to the vault owner.

## Recommended Mitigation Steps
Liquidations should only occur during the auction time. If `settle` is called after auction time (maybe with a small buffer to give liquidators the chance to fully liquidate all collateral at `elapsed >= auctionTime`), it should restore the original owner and it must be grabbed again by the witch (this also performs a collateralization `level` check again in `grab`, which is good).
