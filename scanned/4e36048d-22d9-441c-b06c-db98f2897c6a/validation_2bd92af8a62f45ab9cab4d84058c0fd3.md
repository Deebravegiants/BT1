### Title
Stale Cross-Chain Rate Used for rsETH Minting With No Freshness Guard — (`contracts/cross-chain/CrossChainRateReceiver.sol`)

---

### Summary

`CrossChainRateReceiver.getRate()` returns the last stored `rate` unconditionally. The contract records `lastUpdated` on every `lzReceive` call but never uses it to enforce a freshness window. `RSETHPoolV2.deposit()` calls this function directly to compute the mint amount, so any period of LayerZero relay inactivity causes deposits to be priced against a stale rate.

---

### Finding Description

`CrossChainRateReceiver` stores two state variables relevant here:

- `rate` — the last received rsETH/ETH exchange rate
- `lastUpdated` — the timestamp of the last `lzReceive` call [1](#0-0) 

`lzReceive` updates both on every successful relay: [2](#0-1) 

`getRate()` returns `rate` with no check against `lastUpdated`: [3](#0-2) 

`RSETHPoolV2.viewSwapRsETHAmountAndFee()` calls `getRate()` and uses the result directly to compute the mint amount: [4](#0-3) 

`deposit()` calls `viewSwapRsETHAmountAndFee()` and mints the resulting amount: [5](#0-4) 

There is no staleness guard anywhere in this call chain. The `lastUpdated` field exists but is purely informational.

---

### Impact Explanation

Two mispricing directions are possible:

1. **Stale-low rate** (L1 `rsETHPrice` has risen, relay delayed): `rsETHAmount = amountAfterFee * 1e18 / staleRate` yields more rsETH than the current backing justifies, over-minting and diluting existing holders.
2. **Stale-high rate** (L1 `rsETHPrice` has fallen, relay delayed): the formula yields fewer rsETH than the current rate would produce, meaning the user receives less than the protocol's own rate promises.

Both cases constitute failure to deliver promised returns. No funds are permanently lost, matching the **Low** scope.

---

### Likelihood Explanation

LayerZero relays are not guaranteed to be instantaneous. Network congestion, relay operator downtime, or simply infrequent `updateRate` calls on the provider side can leave the receiver stale for hours or days. `RSETHMultiChainRateProvider.getLatestRate()` reads live from `ILRTOracle.rsETHPrice()`: [6](#0-5) 

but that value only reaches the receiver when a relay is triggered. rsETH accrues yield continuously, so even moderate relay gaps produce measurable divergence.

---

### Recommendation

Add a configurable `maxStaleness` parameter to `CrossChainRateReceiver` and revert in `getRate()` if `block.timestamp - lastUpdated > maxStaleness`:

```solidity
uint256 public maxStaleness; // e.g. 24 hours

function getRate() external view returns (uint256) {
    require(
        lastUpdated != 0 && block.timestamp - lastUpdated <= maxStaleness,
        "Rate is stale"
    );
    return rate;
}
```

This causes `RSETHPoolV2.deposit()` to revert rather than mint at a stale price, protecting both depositors and existing holders until a fresh relay arrives.

---

### Proof of Concept

```solidity
// Fork test (local, no mainnet)
function test_staleRateMispricing() public {
    // 1. Deploy mock LZ endpoint, RSETHRateReceiver, RSETHPoolV2
    // 2. lzReceive delivers initial rate = 1.05e18 (rsETH worth 1.05 ETH)
    assertEq(receiver.rate(), 1.05e18);

    // 3. Warp 24 hours — no new lzReceive call
    vm.warp(block.timestamp + 24 hours);

    // 4. Simulate L1 rsETHPrice now = 1.06e18 (yield accrued)
    // receiver.rate() still returns 1.05e18

    // 5. User deposits 1 ETH
    uint256 minted = pool.viewSwapRsETHAmountAndFee(1e18);
    // minted ≈ 1e18 * 1e18 / 1.05e18 ≈ 0.952e18 rsETH (stale)
    // correct would be: 1e18 * 1e18 / 1.06e18 ≈ 0.943e18 rsETH
    // user receives ~0.009e18 rsETH MORE than current backing justifies

    assertGt(minted, 1e18 * 1e18 / 1.06e18);
}
```

The divergence grows linearly with both the staleness duration and the rate of rsETH yield accrual.

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L13-14)
```text
    uint256 public rate;

```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L95-97)
```text
        rate = _rate;

        lastUpdated = block.timestamp;
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L103-105)
```text
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/pools/RSETHPoolV2.sol (L207-216)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused limitDailyMint(msg.value) {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);
```

**File:** contracts/pools/RSETHPoolV2.sol (L229-233)
```text
        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

**File:** contracts/cross-chain/RSETHMultiChainRateProvider.sol (L26-28)
```text
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
    }
```
