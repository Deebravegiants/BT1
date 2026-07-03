### Title
Stale Cross-Chain Rate Used Without Freshness Check Allows Over-Minting of wrsETH - (File: `contracts/cross-chain/CrossChainRateReceiver.sol`)

---

### Summary

`CrossChainRateReceiver.getRate()` returns the stored `rate` with no staleness check, despite tracking `lastUpdated`. Both `RSETHPoolV3` and `RSETHPoolV3ExternalBridge` use this rate directly to compute how much wrsETH to mint for depositors. When the keeper fails to call `updateRate()` in a timely manner, the L2 oracle rate lags behind the true L1 rate, allowing depositors to mint excess wrsETH at a stale (lower) price.

---

### Finding Description

The cross-chain rate propagation system works as follows:

1. A keeper calls `MultiChainRateProvider.updateRate()` on L1, which fetches the current `rsETHPrice()` from `LRTOracle` and sends it via LayerZero to all registered `CrossChainRateReceiver` contracts on L2.
2. `CrossChainRateReceiver.lzReceive()` stores the received rate and records `lastUpdated = block.timestamp`.
3. L2 pool contracts call `CrossChainRateReceiver.getRate()` to price deposits.

The critical gap is in `CrossChainRateReceiver.getRate()`:

```solidity
// contracts/cross-chain/CrossChainRateReceiver.sol L103-105
function getRate() external view returns (uint256) {
    return rate;
}
```

The `lastUpdated` field (line 16) is stored but **never consulted** in `getRate()`. There is no maximum-age check, no revert on staleness, and no circuit-breaker.

`MultiChainRateProvider.updateRate()` is permissionless but requires the caller to supply ETH to cover LayerZero messaging fees:

```solidity
// contracts/cross-chain/MultiChainRateProvider.sol L108
function updateRate() external payable nonReentrant {
```

There is no on-chain enforcement of update frequency, no incentive reward for callers (unlike Olympus's `beat()` reward), and no fallback that forces an update before a deposit is processed.

Both pool contracts consume this rate without any freshness guard:

```solidity
// contracts/pools/RSETHPoolV3.sol L235-237
function getRate() public view returns (uint256) {
    return IOracle(rsETHOracle).getRate();
}
```

```solidity
// contracts/pools/RSETHPoolV3.sol L299-308
function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
    fee = amount * feeBps / 10_000;
    uint256 amountAfterFee = amount - fee;
    uint256 rsETHToETHrate = getRate();
    rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
}
```

Because rsETH is a yield-bearing token, its ETH-denominated rate increases monotonically over time. A stale (lower) rate causes the division `amountAfterFee * 1e18 / rsETHToETHrate` to produce a **larger** rsETH amount than the deposited ETH actually warrants at the current true rate.

The same pattern is present in `RSETHPoolV3ExternalBridge`:

```solidity
// contracts/pools/RSETHPoolV3ExternalBridge.sol L418-427
function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
    ...
    uint256 rsETHToETHrate = getRate();
    rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
}
```

---

### Impact Explanation

rsETH accrues staking yield continuously on L1. If the L2 oracle rate is stale by even a few days, the gap between the stored rate and the true rate can be meaningful (e.g., ~4–5% annualized staking yield = ~0.01% per day). A depositor who deposits during a stale window receives wrsETH tokens that, once the oracle is updated, are immediately worth more than the ETH deposited. This constitutes **theft of unclaimed yield** from existing wrsETH holders, whose proportional claim on the underlying ETH pool is diluted by the over-minted supply.

**Impact: High — Theft of unclaimed yield.**

---

### Likelihood Explanation

`updateRate()` requires the caller to pay LayerZero cross-chain messaging fees in ETH. There is no on-chain reward for doing so and no enforcement of a minimum update cadence. Keeper downtime, gas price spikes, or LayerZero congestion can all cause the rate to go stale. An attacker who monitors the L1 rate vs. the L2 stored rate can identify windows of staleness and deposit opportunistically. The attack requires no special privileges and is executable by any depositor.

**Likelihood: Medium.**

---

### Recommendation

1. **Add a staleness check in `getRate()`**: Revert (or return a sentinel) if `block.timestamp - lastUpdated` exceeds a configurable `maxStaleness` threshold (e.g., 24 hours).

```solidity
uint256 public maxStaleness = 24 hours;

function getRate() external view returns (uint256) {
    require(block.timestamp - lastUpdated <= maxStaleness, "Rate is stale");
    return rate;
}
```

2. **Enforce freshness in pool deposit paths**: Both `RSETHPoolV3` and `RSETHPoolV3ExternalBridge` should propagate the revert from a stale oracle rather than silently using an outdated rate.

3. **Consider an on-chain incentive or keeper bond** for `updateRate()` callers, analogous to the Olympus `Heart` reward, to ensure timely updates.

---

### Proof of Concept

1. At time T=0, the L1 rsETH rate is `1.050e18` (1.05 ETH per rsETH). The L2 oracle is updated: `CrossChainRateReceiver.rate = 1.050e18`, `lastUpdated = T`.
2. The keeper goes offline. Over 30 days, the L1 rate grows to `1.054e18` (staking yield).
3. At T+30d, an attacker calls `RSETHPoolV3.deposit{value: 10 ether}("")`.
4. `viewSwapRsETHAmountAndFee(10e18)` reads `rsETHToETHrate = 1.050e18` (stale).
5. `rsETHAmount = 10e18 * 1e18 / 1.050e18 ≈ 9.5238 wrsETH`.
6. At the true rate `1.054e18`, the correct amount is `10e18 * 1e18 / 1.054e18 ≈ 9.4876 wrsETH`.
7. The attacker receives `≈ 0.0362 wrsETH` excess — immediately redeemable for more ETH than deposited once the oracle is refreshed.
8. Scaled to the daily mint limit, this excess compounds across all depositors during the stale window.

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L13-16)
```text
    uint256 public rate;

    /// @notice Last time rate was updated
    uint256 public lastUpdated;
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L102-105)
```text
    /// @notice Gets the last stored rate in the contract
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L108-137)
```text
    function updateRate() external payable nonReentrant {
        uint256 latestRate = getLatestRate();

        rate = latestRate;

        lastUpdated = block.timestamp;

        bytes memory _payload = abi.encode(latestRate);

        uint256 rateReceiversLength = rateReceivers.length;

        for (uint256 i; i < rateReceiversLength;) {
            uint16 dstChainId = uint16(rateReceivers[i]._chainId);

            bytes memory remoteAndLocalAddresses = abi.encodePacked(rateReceivers[i]._contract, address(this));

            (uint256 estimatedFee,) = ILayerZeroEndpoint(layerZeroEndpoint)
                .estimateFees(dstChainId, address(this), _payload, false, bytes(""));

            ILayerZeroEndpoint(layerZeroEndpoint).send{ value: estimatedFee }(
                dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
            );

            unchecked {
                ++i;
            }
        }

        emit RateUpdated(rate);
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L234-237)
```text
    /// @dev Gets the rate from the rsETHOracle
    function getRate() public view returns (uint256) {
        return IOracle(rsETHOracle).getRate();
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L299-308)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L418-427)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
    }
```
