# [M] Supply function doesn’t account for market maxDeposit when providing assets to it

## Summary
Severity: Medium
Contest weight: 0.5104
Dataset id: 2345
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Some vaults that the Silo vault deposits into have their own supply caps (do not confuse with `config[market].cap`), which may prevent `_supplyERC4626` from fully depositing user-provided assets. If these caps are not accounted for, the deposit function may revert instead of distributing assets across multiple vaults.

## Proof of Concept
Consider a scenario where there are two vaults available for deposits:

  * Vault 1 has a supply cap of 10,000 assets and currently holds 5,000, meaning `vault1.maxDeposit` is 10,000 - 5,000 = 5,000.
  * Vault 2 is in the same condition.

In total, 10,000 assets of deposit space are available. However, if a user tries to deposit 10,000 assets through the Silo vault, `_supplyERC4626` is called:

```solidity
function _supplyERC4626(uint256 _assets) internal virtual {
    for (uint256 i; i < supplyQueue.length; ++i) {
        IERC4626 market = supplyQueue[i];

        uint256 supplyCap = config[market].cap;
        if (supplyCap == 0) continue;

        // Update internal balance for market to include interest if any.
        // `supplyAssets` needs to be rounded up for `toSupply` to be rounded down.
        uint256 supplyAssets = _updateInternalBalanceForMarket(market);

        uint256 toSupply = UtilsLib.min(UtilsLib.zeroFloorSub(supplyCap, supplyAssets), _assets);

        if (toSupply != 0) {
            uint256 newBalance = balanceTracker[market] + toSupply;
            // As `_supplyBalance` reads the balance directly from the market,
            // we have additional check to ensure that the market did not report wrong supply.
            if (newBalance <= supplyCap) {
                // Using try/catch to skip markets that revert.
                try market.deposit(toSupply, address(this)) {
                    _assets -= toSupply;
                    balanceTracker[market] = newBalance;
                } catch {}
            }
        }

        if (_assets == 0) return;
    }
}
```

The function will first attempt to deposit 10,000 assets into Vault 1, but since `vault1.maxDeposit` < 10,000, the transaction will revert. The same issue occurs with Vault 2, causing the entire deposit operation to fail—even though sufficient space exists across both vaults.

## Recommendation
No recommendation
