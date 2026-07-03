### Title
Public `updateRSETHPrice()` Triggers Automatic Multi-Contract Pause With Manual-Only Recovery — (File: `contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle.updateRSETHPrice()` is an unrestricted public function. When the computed rsETH price falls below the all-time-high by more than `pricePercentageLimit`, it automatically pauses `LRTDepositPool`, `LRTWithdrawalManager`, and `LRTOracle` itself in a single call. Restoring the protocol requires the admin to manually unpause each of the three contracts in separate transactions. Any unprivileged caller can trigger this freeze whenever market conditions satisfy the threshold.

---

### Finding Description

`updateRSETHPrice()` carries no access-control modifier:

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
``` [1](#0-0) 

Inside `_updateRsETHPrice()`, the downside-protection branch executes unconditionally for any caller:

```solidity
if (isPriceDecreaseOffLimit) {
    if (!lrtDepositPool.paused()) lrtDepositPool.pause();
    if (!withdrawalManager.paused()) withdrawalManager.pause();
    _pause();
    return;
}
``` [2](#0-1) 

The condition is:

```solidity
bool isPriceDecreaseOffLimit =
    pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);
``` [3](#0-2) 

`pricePercentageLimit` is a non-zero admin-configured value (its purpose is downside protection, so it is expected to be set in production). `highestRsethPrice` is the all-time-high price stored on-chain and never decreases. Any transient drop in the underlying LST oracle rates — even one that self-corrects within minutes — satisfies the condition and allows any public caller to atomically pause all three contracts.

Unpausing each contract requires a separate `onlyLRTAdmin` transaction:

- `LRTOracle.unpause()` — `onlyLRTAdmin`
- `LRTDepositPool.unpause()` — `onlyLRTAdmin`
- `LRTWithdrawalManager.unpause()` — `onlyLRTAdmin` [4](#0-3) [5](#0-4) 

While the oracle is paused, `updateRSETHPrice()` reverts with `ContractPaused`, so the price cannot be refreshed until the admin acts. The admin must also investigate whether the price drop was genuine or transient before deciding to unpause, adding further latency.

---

### Impact Explanation

Both deposits (`LRTDepositPool`) and withdrawals (`LRTWithdrawalManager`) are frozen simultaneously. Users cannot enter or exit the protocol until the admin manually issues three separate unpause transactions. This constitutes a **temporary freezing of funds** matching the allowed Medium impact scope.

---

### Likelihood Explanation

`updateRSETHPrice()` is callable by any EOA or contract. LST oracle rates (stETH/ETH, cbETH/ETH, etc.) fluctuate intra-day. A transient dip that crosses the configured `pricePercentageLimit` — or a deliberate oracle-rate read at a momentarily unfavorable block — is sufficient. No capital, no special role, and no prior state is required beyond the threshold being crossed. The attacker's only cost is gas.

---

### Recommendation

1. **Restrict the public entry point.** Gate `updateRSETHPrice()` to `onlyLRTManager` (or a keeper role), matching the existing `updateRSETHPriceAsManager()` pattern. The manager variant already exists precisely to handle edge cases; the unrestricted public variant adds no user-facing value that justifies the risk.
2. **Separate the pause trigger from the price-update path.** Emit an event and let an off-chain keeper or a dedicated `pauseIfPriceOffLimit()` function (still restricted) handle the pause decision, rather than embedding it inside the price-update hot path.
3. **Provide a single `unpauseAll()` admin function** analogous to the existing `LRTConfig.pauseAll()`, so recovery is a single atomic transaction rather than three sequential ones.

---

### Proof of Concept

1. Admin sets `pricePercentageLimit = 1e16` (1 %).
2. `highestRsethPrice` is recorded at `1.05 ether` after a period of rewards.
3. A transient stETH oracle dip causes `_getTotalEthInProtocol()` to return a value that prices rsETH at `1.034 ether` — a ~1.5 % drop from the peak.
4. Attacker calls `LRTOracle.updateRSETHPrice()` (no role required).
5. `diff = 1.05e18 - 1.034e18 = 0.016e18`; `pricePercentageLimit.mulWad(1.05e18) = 0.0105e18`; `0.016e18 > 0.0105e18` → `isPriceDecreaseOffLimit = true`.
6. `LRTDepositPool`, `LRTWithdrawalManager`, and `LRTOracle` are all paused in the same transaction.
7. All user deposits and withdrawals revert. The oracle cannot be updated. The admin must issue three separate `unpause()` calls to restore the protocol. [1](#0-0) [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L143-146)
```text
    function unpause() external whenPaused onlyLRTAdmin {
        paused = false;
        emit Unpaused(msg.sender);
    }
```

**File:** contracts/LRTOracle.sol (L269-282)
```text
        // downside protection — pause if price drops too far
        if (newRsETHPrice < highestRsethPrice) {
            uint256 diff = highestRsethPrice - newRsETHPrice;
            // normalizing to 1e18
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

            // if price decrease is off limit, pause the protocol (unless it's already paused)
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
            }
```

**File:** contracts/LRTOracle.sol (L331-349)
```text
    function _getTotalEthInProtocol() private view returns (uint256 totalETHInProtocol) {
        address lrtDepositPoolAddr = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
        address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
        uint256 supportedAssetCount = supportedAssets.length;

        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);

            unchecked {
                ++assetIdx;
            }
        }
    }
```

**File:** contracts/LRTDepositPool.sol (L353-356)
```text
    /// @dev Returns to normal state. Contract must be paused.
    function unpause() external onlyLRTAdmin {
        _unpause();
    }
```
