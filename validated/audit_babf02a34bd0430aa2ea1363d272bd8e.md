Audit Report

## Title
Unaccounted L1Vault Assets Cause rsETH Price Understatement, Enabling Share Dilution Attack - (File: contracts/LRTDepositPool.sol, contracts/LRTOracle.sol)

## Summary
Assets (ETH and LSTs) bridged from L2 and held in `L1Vault` contracts are never included in `LRTDepositPool.getTotalAssetDeposits()`. Because `LRTOracle.updateRSETHPrice()` is a public, permissionless function, an attacker can trigger a price update while `L1Vault` holds undeposited assets, causing `rsETHPrice` to be set below its true value. The attacker then deposits at the artificially low price, receiving more rsETH than deserved and diluting existing holders.

## Finding Description
`LRTOracle._getTotalEthInProtocol()` computes total ETH backing rsETH by iterating over supported assets and calling `ILRTDepositPool.getTotalAssetDeposits(asset)` for each. `getTotalAssetDeposits` delegates to `getAssetDistributionData` (for LSTs) and `getETHDistributionData` (for ETH).

`getETHDistributionData()` (lines 467–500 of `LRTDepositPool.sol`) accounts for:
- `LRTDepositPool.balance`
- Each NDC's ETH balance
- EigenLayer pod shares
- Unstaking ETH
- `LRTUnstakingVault.balance`
- `LRTConverter.ethValueInWithdrawal()`

`getAssetDistributionData()` (lines 426–462 of `LRTDepositPool.sol`) accounts for:
- `LRTDepositPool` token balance
- Each NDC's token balance
- EigenLayer strategy shares
- Unstaking LST amounts
- `LRTUnstakingVault` token balance

**`L1Vault` is absent from both lists.** `L1Vault` accepts ETH via its `receive()` function (line 368 of `L1Vault.sol`) and holds LSTs until a manager manually calls `depositETHForL1VaultETH()` or `depositAssetForL1Vault()` (lines 150 and 166 of `L1Vault.sol`), both of which are `onlyRole(MANAGER_ROLE)`. Between bridge arrival and manager processing, those assets are invisible to `_getTotalEthInProtocol()`.

`updateRSETHPrice()` is public and permissionless (line 87 of `LRTOracle.sol`):
```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

The price is computed as (line 250 of `LRTOracle.sol`):
```solidity
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

With L1Vault assets excluded, `totalETHInProtocol` is understated, so `newRsETHPrice` is set below its true value.

The minting formula (line 520 of `LRTDepositPool.sol`):
```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

A lower `rsETHPrice` denominator yields a larger `rsethAmountToMint`.

The downside protection in `_updateRsETHPrice()` (lines 270–282 of `LRTOracle.sol`) only pauses the protocol if `pricePercentageLimit > 0` and the price drop exceeds `pricePercentageLimit.mulWad(highestRsethPrice)`. If `pricePercentageLimit` is zero or the L1Vault balance is small relative to TVL (keeping the drop within the configured limit), the manipulated price is written and deposits proceed normally.

## Impact Explanation
**High — Theft of unclaimed yield.** When the attacker deposits at the artificially low `rsETHPrice`, they receive excess rsETH shares. Once the manager calls `depositETHForL1VaultETH()` or `depositAssetForL1Vault()`, the true TVL is restored and `rsETHPrice` rises back to its correct level. The attacker's excess shares now represent a claim on assets they did not contribute, directly diluting all existing rsETH holders. The profit scales with both the attacker's deposit size and the magnitude of the L1Vault balance relative to total TVL.

## Likelihood Explanation
**Medium.** The L1Vault holding undeposited assets is a routine operational state — assets arrive from L2 bridges continuously and are processed by the manager in batches. The protocol operates across many L2 chains (Arbitrum, Optimism, Scroll, Blast, Mode, etc.), each with its own L1Vault, so the aggregate unaccounted balance can be material. The attacker only needs to monitor L1Vault balances on-chain and call the public `updateRSETHPrice()` at the right moment before the manager acts. No special privileges are required.

## Recommendation
Include the balances of all registered `L1Vault` contracts in `getETHDistributionData()` and `getAssetDistributionData()`. Maintain a registry of L1Vault addresses in `LRTConfig` and sum their ETH and LST balances alongside the existing accounting locations. Alternatively, restrict `updateRSETHPrice()` to a privileged role (manager/operator), removing the permissionless attack vector entirely.

## Proof of Concept
1. A large ETH transfer arrives at `L1Vault` from the Arbitrum bridge (e.g., 500 ETH). The manager has not yet called `depositETHForL1VaultETH()`.
2. Attacker calls `LRTOracle.updateRSETHPrice()`. `_getTotalEthInProtocol()` sums all tracked locations but misses the 500 ETH in L1Vault. Suppose true TVL is 10,000 ETH and rsETH supply is 9,500; true price ≈ 1.0526 ETH/rsETH. With 500 ETH missing, computed price ≈ 1.0000 ETH/rsETH. `rsETHPrice` is written as ~1.0000 (price drop of ~5%; if `pricePercentageLimit` is 0 or ≥ 5%, the write succeeds).
3. Attacker immediately calls `LRTDepositPool.depositETH()` with 100 ETH. `rsethAmountToMint = 100e18 * 1e18 / 1.0000e18 = 100 rsETH` instead of the correct `~95 rsETH`.
4. Manager calls `depositETHForL1VaultETH()`, depositing 500 ETH. Next `updateRSETHPrice()` call restores price to ~1.0526.
5. Attacker holds 100 rsETH worth ~105.26 ETH, having deposited only 100 ETH — a ~5.26 ETH gain extracted from existing holders.

**Foundry fork test plan:** Fork mainnet, deploy/configure L1Vault with a funded balance, call `updateRSETHPrice()` as an unprivileged address, assert `rsETHPrice` is below the pre-fork value, deposit as attacker, then call `depositETHForL1VaultETH()` as manager and `updateRSETHPrice()` again, assert attacker's rsETH redemption value exceeds their deposit.