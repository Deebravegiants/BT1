### Title
Stale Cross-Chain Rate Used Without Staleness Validation Allows Over-Minting of wrsETH - (File: `contracts/cross-chain/CrossChainRateReceiver.sol`)

---

### Summary

`CrossChainRateReceiver` stores a `lastUpdated` timestamp every time a new rate is received via LayerZero, but `getRate()` returns the stored `rate` unconditionally without ever checking whether the rate has become stale. L2 pool contracts (`RSETHPoolV2`, `RSETHPoolV3`, etc.) call `getRate()` to determine how many wrsETH tokens to mint per unit of ETH deposited. When the L1 rsETH price rises and the L2 rate lags behind, any depositor can exploit the stale (artificially low) rate to receive more wrsETH than the current exchange rate warrants, at the expense of existing wrsETH holders.

---

### Finding Description

`CrossChainRateReceiver.lzReceive()` records the rate and the time it was received:

```solidity
// contracts/cross-chain/CrossChainRateReceiver.sol
rate = _rate;
lastUpdated = block.timestamp;   // stored but never read again
```

`getRate()` ignores `lastUpdated` entirely:

```solidity
function getRate() external view returns (uint256) {
    return rate;   // no staleness check
}
```

Every L2 deposit pool calls this function to price new deposits:

```solidity
// contracts/pools/RSETHPoolV2.sol  (identical pattern in V3, ExternalBridge variants)
function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
    fee = amount * feeBps / 10_000;
    uint256 amountAfterFee = amount - fee;
    uint256 rsETHToETHrate = getRate();          // stale rate accepted silently
    rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
}
```

Because `rsETHAmount` is inversely proportional to `rsETHToETHrate`, a stale rate that is lower than the true current rate causes the pool to mint more wrsETH per ETH than it should. The `lastUpdated` field is the direct analog of `depositDetail.optionsRenewedTimeStamp` in the reference report: it exists in storage, it is written on every update, but it is never read back to gate the benefit it is supposed to time-bound.

---

### Impact Explanation

When the L1 rsETH price appreciates and the L2 rate has not yet been refreshed (LayerZero message delayed, `updateRate()` not called, or network congestion), an attacker deposits ETH at the stale lower rate and receives a proportionally larger wrsETH balance. Upon redemption, that wrsETH is worth more rsETH than the deposited ETH warranted at the true rate. The surplus comes directly from the pool's rsETH reserves, diluting or directly reducing the redemption value available to all other wrsETH holders. This constitutes theft of user funds held in the pool.

**Impact class**: High — theft of unclaimed yield / value from existing wrsETH holders; can escalate to Critical if the rate lag is large or the deposit is large.

---

### Likelihood Explanation

LayerZero message delivery is not instantaneous and `updateRate()` must be called manually (or by a keeper) on the provider side. Any period during which the L1 rsETH price rises faster than the cross-chain update cadence creates the exploitable window. An attacker needs only to monitor the L1 oracle price versus the L2 stored rate and deposit when the gap is profitable. No privileged access is required; the `deposit()` function is fully public.

---

### Recommendation

Add a configurable `maxStaleness` parameter and revert in `getRate()` if the rate is too old:

```solidity
uint256 public maxStaleness; // e.g. 24 hours

function getRate() external view returns (uint256) {
    require(block.timestamp - lastUpdated <= maxStaleness, "Rate is stale");
    return rate;
}
```

Alternatively, pause deposits on the L2 pool automatically when the rate has not been refreshed within the expected window.

---

### Proof of Concept

1. At time T₀, L1 rsETH price = 1.05 ETH. LayerZero pushes this rate to `CrossChainRateReceiver`; `rate = 1.05e18`, `lastUpdated = T₀`.
2. At time T₁ = T₀ + 48 h, L1 rsETH price rises to 1.10 ETH. No `updateRate()` call has been made; L2 `rate` is still `1.05e18`.
3. Attacker calls `RSETHPoolV2.deposit{value: 100 ether}("")`.
4. `viewSwapRsETHAmountAndFee(100 ether)` computes `rsETHAmount = 100e18 * 1e18 / 1.05e18 ≈ 95.24 wrsETH`.
5. Correct amount at current rate would be `100e18 * 1e18 / 1.10e18 ≈ 90.91 wrsETH`.
6. Attacker receives **≈ 4.33 excess wrsETH** (≈ 4.76% over-mint) per 100 ETH deposited.
7. After the rate is updated to 1.10, attacker redeems 95.24 wrsETH for ≈ 104.76 ETH worth of rsETH, profiting at the expense of other holders. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L93-105)
```text
        uint256 _rate = abi.decode(_payload, (uint256));

        rate = _rate;

        lastUpdated = block.timestamp;

        emit RateUpdated(_rate);
    }

    /// @notice Gets the last stored rate in the contract
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/pools/RSETHPoolV2.sol (L225-234)
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
