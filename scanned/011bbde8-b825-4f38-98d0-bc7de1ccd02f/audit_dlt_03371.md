# [M] Witch lock vault waiting for better price

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-05-yield
Published: 2021-06-02
Source: https://github.com/code-423n4/2021-05-yield-findings/issues/64
Type: code-finding

## Details
# Handle

a_delamo


# Vulnerability details

## Impact

On the Witch, you can grab any under collateralized vault for X amount of time without requiring any payment of collateral.

```
 function grab(bytes12 vaultId) public {
        DataTypes.Vault memory vault = cauldron.vaults(vaultId);
        vaultOwners[vaultId] = vault.owner;
        cauldron.grab(vaultId, address(this));
    }

```

We also have the payment method used by the liquidators. Where the price the liquidators need to pay gets reduced with time. 
So, don't you think the incentive of the liquidators will be to wait as much as possible?
Even using MEV to renovate the grab without doing anything? Blocking other liquidators who really want to bring liquidity to the protocol?

```
    /// @dev Buy an amount of collateral off a vault in liquidation, paying at most `max` underlying.
    function buy(
        bytes12 vaultId,
        uint128 art,
        uint128 min
    ) public {
        DataTypes.Balances memory balances_ = cauldron.balances(vaultId);

        require(balances_.art > 0, "Nothing to buy"); // Cheapest way of failing gracefully if given a non existing vault
        uint256 elapsed = uint32(block.timestamp) - cauldron.auctions(vaultId); // Auctions will malfunction on the 7th of February 2106, at 06:28:16 GMT, we should replace this contract before then.
        uint256 price;
        {
            // Price of a collateral unit, in underlying, at the present moment, for a given vault
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2021-05-yield-findings/issues/64_
