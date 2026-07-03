### Title
Block Stuffing Enables Stale-Price Ratchet of `highestRsethPrice`, Triggering Spurious Auto-Pause — (`contracts/oracles/ChainlinkPriceOracle.sol`, `contracts/LRTOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice` contains no staleness check on the Chainlink round data. An attacker can stuff blocks to prevent oracle heartbeat updates, call the public `updateRSETHPrice` while the stale-high price is live, ratchet `highestRsethPrice` to an inflated value, and then — once blocks resume and the oracle corrects — trigger the downside-protection auto-pause on the next legitimate price update, even though no real loss occurred.

---

### Finding Description

**Root cause 1 — No staleness check in `ChainlinkPriceOracle.getAssetPrice`:**

`getAssetPrice` calls `latestRoundData()` but discards `updatedAt` and `answeredInRound`, accepting any price regardless of age.

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

**Root cause 2 — `updateRSETHPrice` is permissionless:**

Any address can call it at any time while the contract is not paused. [2](#0-1) 

**Root cause 3 — `highestRsethPrice` ratchets up monotonically:**

When `newRsETHPrice > highestRsethPrice`, the peak is updated with no validation that the underlying oracle data is fresh. [3](#0-2) 

**Root cause 4 — Downside protection compares against the ratcheted peak:**

If the next computed price falls more than `pricePercentageLimit` below `highestRsethPrice`, the protocol auto-pauses. [4](#0-3) 

**Attack sequence:**

1. Attacker stuffs every block for the Chainlink heartbeat window, preventing the feed from updating. The feed retains a stale-high price (e.g., reflecting a temporary spike or simply the previous round's value before a real decline).
2. Attacker calls `updateRSETHPrice()`. `_getTotalEthInProtocol()` reads the stale-high price, inflating `totalETHInProtocol` and therefore `newRsETHPrice`.
3. Because `newRsETHPrice > highestRsethPrice`, line 295 sets `highestRsethPrice` to the inflated value.
4. Block stuffing ends; Chainlink updates to the true (lower) price.
5. Any caller invokes `updateRSETHPrice()` again. `newRsETHPrice` now reflects the true TVL — lower than the artificially ratcheted `highestRsethPrice`.
6. If the gap exceeds `pricePercentageLimit * highestRsethPrice`, lines 278–281 pause `LRTDepositPool`, `LRTWithdrawalManager`, and `LRTOracle`, freezing all user deposits and withdrawals.

---

### Impact Explanation

The auto-pause freezes deposits and withdrawals for all users until an admin manually unpauses. The `highestRsethPrice` ratchet is permanent — it does not decay — so the inflated peak remains as the comparison baseline for all future price updates, permanently lowering the threshold at which a future legitimate price movement triggers another spurious pause. This constitutes **temporary (and potentially repeated) freezing of funds**, with the enabling mechanism being **block stuffing**.

---

### Likelihood Explanation

Block stuffing on Ethereum mainnet is expensive but not infeasible for a motivated attacker targeting a high-TVL protocol. Chainlink ETH-denominated feeds typically have a 1-hour heartbeat and a 0.5–1% deviation threshold. Stuffing blocks for a shorter window (e.g., until a natural price spike is locked in as stale) reduces cost significantly. The permissionless `updateRSETHPrice` means the attacker does not need any privileged role — only the ability to fill blocks and submit one transaction.

---

### Recommendation

1. **Add a staleness check** in `ChainlinkPriceOracle.getAssetPrice`: revert if `block.timestamp - updatedAt` exceeds a configured `maxStaleness` threshold.

```solidity
(, int256 price,, uint256 updatedAt,) = priceFeed.latestRoundData();
if (block.timestamp - updatedAt > maxStaleness) revert StalePrice();
```

2. **Guard `highestRsethPrice` updates** by only allowing the ratchet when the oracle data is confirmed fresh (i.e., after the staleness check passes).

3. Consider requiring a **MANAGER role** to call `updateRSETHPrice` directly, or at minimum rate-limiting public calls.

---

### Proof of Concept

```solidity
// State test (local fork or mock environment)
// 1. Deploy mock Chainlink feed returning price P_high (stale).
// 2. Call updateRSETHPrice() → records highestRsethPrice = f(P_high).
// 3. Update mock feed to return true price P_true < P_high,
//    such that (P_high - P_true) / P_high > pricePercentageLimit.
// 4. Call updateRSETHPrice() again.
// 5. Assert: LRTDepositPool.paused() == true  (auto-pause triggered)
//            despite no real loss of TVL having occurred.
```

The test requires no privileged role — only control over the mock oracle (simulating what block stuffing achieves on a live feed) and two public calls to `updateRSETHPrice`.

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L52-54)
```text
        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L270-282)
```text
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

**File:** contracts/LRTOracle.sol (L293-296)
```text
        // update highest price if new price exceeds it
        if (newRsETHPrice > highestRsethPrice) {
            highestRsethPrice = newRsETHPrice;
        }
```
