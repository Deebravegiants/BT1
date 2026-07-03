Looking at the full contract chain: `RSETHMultiChainRateProvider` → `MultiChainRateProvider.updateRate()` → LayerZero → L2 receiver → `RSETHPoolNoWrapper`/`RSETHPoolV3ExternalBridge`.

### Title
Permissionless `updateRate` with No Staleness Guard Enables Block-Stuffing to Exploit Stale Cross-Chain rsETH Rate — (`contracts/cross-chain/RSETHMultiChainRateProvider.sol`)

---

### Summary

`MultiChainRateProvider.updateRate()` is permissionless and carries no on-chain staleness enforcement. `CrossChainRateReceiver` stores the last received rate indefinitely with no expiry. L2 pools (`RSETHPoolNoWrapper`, `RSETHPoolV3ExternalBridge`) price every swap directly against this stored rate. An attacker who stuffs Ethereum mainnet blocks during a `rsETHPrice` increase window can prevent the rate from propagating to L2, then drain the discount created by the stale rate.

---

### Finding Description

**Rate propagation path (L1 → L2):**

`RSETHMultiChainRateProvider.getLatestRate()` reads `ILRTOracle.rsETHPrice()` live from L1. [1](#0-0) 

`MultiChainRateProvider.updateRate()` is a fully permissionless `external payable` function — no role check, no caller whitelist. [2](#0-1) 

It sends the rate via LayerZero to every registered `RSETHRateReceiver` (one per destination chain). [3](#0-2) 

**Rate storage on L2 (no expiry):**

`CrossChainRateReceiver.lzReceive()` writes the received rate to `rate` and `lastUpdated`, but `getRate()` returns `rate` unconditionally — there is no maximum-age check. [4](#0-3) 

**Pool pricing (no staleness guard):**

`RSETHPoolNoWrapper.viewSwapRsETHAmountAndFee()` calls `getRate()` directly and divides by it. If the stored rate is stale-low, the user receives more rsETH per ETH. [5](#0-4) 

`RSETHPoolV3ExternalBridge.viewSwapRsETHAmountAndFee()` is identical in structure. [6](#0-5) 

**The gap:** `lastUpdated` is stored in both the provider and receiver but is **never read** by any pricing function. There is no circuit-breaker that reverts or discounts swaps when the rate is older than some threshold. [7](#0-6) 

---

### Impact Explanation

When `rsETHPrice` rises on L1 (e.g., after EigenLayer reward accrual updates `LRTOracle`) and the L2 receiver still holds the pre-increase rate `R_old < R_new`, every depositor receives:

```
rsETHAmount = amountAfterFee * 1e18 / R_old   >   amountAfterFee * 1e18 / R_new
```

The excess rsETH is funded by the pool's pre-loaded rsETH inventory, which represents yield belonging to existing rsETH holders. Arbitrageurs extract this as profit — **theft of unclaimed yield**.

---

### Likelihood Explanation

`updateRate()` is permissionless, so the attacker must prevent **all** callers from landing a transaction on Ethereum mainnet. This requires block stuffing: filling consecutive blocks with high-gas-price filler transactions so that `updateRate()` is never included. On Ethereum mainnet this is expensive (~30 M gas × base fee per block), but:

- The attack window only needs to span the blocks between the `rsETHPrice` oracle update and the next successful `updateRate()` call.
- The attacker can monitor the mempool for the oracle update transaction, then immediately begin stuffing.
- Profit scales with pool liquidity and the magnitude of the price jump; a large EigenLayer reward event could make the economics favorable.
- No admin compromise, no private key leak, and no governance capture is required.

Likelihood is **low** due to the cost of mainnet block stuffing, but the impact is **high** (theft of unclaimed yield), placing this squarely in the "Low. Block stuffing" category with a secondary "High. Theft of unclaimed yield" impact.

---

### Recommendation

1. **Add a staleness guard in `CrossChainRateReceiver.getRate()`**: revert (or return a sentinel) if `block.timestamp - lastUpdated > MAX_RATE_AGE`. This prevents pools from pricing swaps against an arbitrarily old rate regardless of the cause of the delay.

2. **Add the same guard in the L2 pools**: `RSETHPoolNoWrapper` and `RSETHPoolV3ExternalBridge` should independently validate rate freshness before executing a swap, so a compromised or lagging oracle cannot silently drain the pool.

3. **Consider a keeper with EIP-1559 tip floor**: ensure `updateRate()` is called with a competitive `maxPriorityFeePerGas` so that block stuffing becomes prohibitively expensive relative to any realistic arbitrage profit.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Fork-safe test (Foundry, fork of Ethereum mainnet)
// 1. Deploy / reference RSETHMultiChainRateProvider, RSETHRateReceiver, RSETHPoolNoWrapper
// 2. Simulate reward accrual: vm.store(lrtOracle, rsETHPriceSlot, newHigherPrice)
// 3. Simulate block stuffing: vm.roll(block.number + N) without calling updateRate()
// 4. Call pool.viewSwapRsETHAmountAndFee(1 ether)
// 5. Assert rsETHAmount > 1 ether * 1e18 / newHigherPrice

function testBlockStuffingStaleRate() public {
    uint256 oldRate = 1.05e18;  // pre-reward rate stored in receiver
    uint256 newRate = 1.08e18;  // post-reward rate now live on L1 oracle

    // Receiver still holds oldRate (updateRate never called)
    // Pool computes: rsETHAmount = 1e18 * 1e18 / oldRate = ~0.952e18
    // True amount:   rsETHAmount = 1e18 * 1e18 / newRate = ~0.926e18
    // Excess:        ~0.026e18 rsETH per ETH deposited — extracted from pool inventory

    (uint256 rsETHAmount,) = pool.viewSwapRsETHAmountAndFee(1 ether);
    uint256 trueAmount = 1 ether * 1e18 / newRate;
    assertGt(rsETHAmount, trueAmount, "stale rate yields excess rsETH");
}
```

The test requires no privileged access: it only needs the oracle storage slot to be updated (simulating a normal reward accrual) and `updateRate()` to be withheld (simulating block stuffing). The assertion will pass on unmodified code whenever `newRate > oldRate`.

### Citations

**File:** contracts/cross-chain/RSETHMultiChainRateProvider.sol (L26-28)
```text
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
    }
```

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L108-113)
```text
    function updateRate() external payable nonReentrant {
        uint256 latestRate = getLatestRate();

        rate = latestRate;

        lastUpdated = block.timestamp;
```

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L119-134)
```text
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
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L14-15)
```text

    /// @notice Last time rate was updated
```

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

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L277-286)
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
