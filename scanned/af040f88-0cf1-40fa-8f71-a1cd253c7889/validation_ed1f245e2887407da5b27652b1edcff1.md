### Title
Stale Cross-Chain Rate in `CrossChainRateReceiver` Allows L2 Depositors to Receive Excess rsETH at Existing Holders' Expense — (File: `contracts/cross-chain/CrossChainRateReceiver.sol`)

---

### Summary

The `CrossChainRateReceiver` stores a `lastUpdated` timestamp alongside the pushed `rate`, but `getRate()` returns the stored rate unconditionally with no staleness validation. All L2 pool contracts consume this rate to calculate how much rsETH to mint per unit of deposited ETH. When the L2 rate lags behind the L1 rate (which increases monotonically as yield accrues), any depositor can exploit the gap to receive more rsETH than their deposit is worth at the current L1 rate, extracting yield that belongs to existing holders.

---

### Finding Description

`CrossChainRateReceiver.getRate()` simply returns `rate` with no check on `lastUpdated`:

```solidity
function getRate() external view returns (uint256) {
    return rate;
}
```

The `lastUpdated` field is written on every `lzReceive` call but is never read by any consumer. [1](#0-0) 

All three L2 pool contracts call `IOracle(rsETHOracle).getRate()` to obtain the rsETH/ETH exchange rate and use it to compute the minting amount:

```solidity
uint256 rsETHToETHrate = getRate();
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
``` [2](#0-1) [3](#0-2) [4](#0-3) 

The L1 `rsETHPrice` is calculated as `totalETHInProtocol / rsethSupply` and increases monotonically as restaking yield accrues. [5](#0-4) 

The rate is pushed to L2 by calling `MultiChainRateProvider.updateRate()`, which is **permissionless** — anyone can call it, but no one is forced to. [6](#0-5) 

When the L2 rate is stale (lower than the current L1 rate), the division `amountAfterFee * 1e18 / rsETHToETHrate` yields a **larger** rsETH amount than the depositor's ETH is worth at the true current rate. The excess rsETH represents yield that should have accrued to existing holders but is instead captured by the late depositor.

---

### Impact Explanation

**High — Theft of unclaimed yield.**

rsETH is a yield-bearing token: its ETH/rsETH rate increases over time as restaking rewards accumulate. Existing holders' share of the protocol's TVL is expressed through the rising rate. When a depositor mints rsETH at a stale (lower) rate, they receive more rsETH than their ETH contribution justifies at the current rate. This dilutes the yield entitlement of all existing rsETH holders — the excess rsETH minted is backed by no additional ETH, so the protocol's per-token ETH value is reduced for everyone else.

The magnitude scales with: (a) how stale the rate is, and (b) the size of the deposit. A depositor who monitors the L2 rate lag and deposits large amounts during a stale window can systematically extract yield from existing holders.

---

### Likelihood Explanation

**Medium.**

Rate updates depend entirely on off-chain infrastructure (a keeper or bot) calling `updateRate()` and paying LayerZero fees. There is no on-chain enforcement of update frequency. Network congestion, keeper downtime, or deliberate inaction can all create stale windows. Since `updateRate()` is permissionless, a sophisticated attacker can also **choose not to update** the rate (by simply not calling it) and deposit during the resulting stale window. The `lastUpdated` variable is stored on-chain and publicly readable, making it trivial to detect when the rate is stale. [7](#0-6) 

---

### Recommendation

Add a configurable `maxStaleness` parameter to `CrossChainRateReceiver` and revert in `getRate()` if `block.timestamp - lastUpdated > maxStaleness`. This mirrors the staleness check pattern used in `ChainlinkOracleForRSETHPoolCollateral` for Chainlink feeds. [8](#0-7) 

```solidity
function getRate() external view returns (uint256) {
    require(block.timestamp - lastUpdated <= maxStaleness, "Rate is stale");
    return rate;
}
```

Additionally, consider requiring a minimum deposit slippage parameter in L2 pool `deposit()` functions (analogous to `minRSETHAmountExpected` in `LRTDepositPool.depositETH()`) so users can protect themselves from receiving fewer tokens than expected when the rate is updated mid-block. [9](#0-8) 

---

### Proof of Concept

1. The L1 rsETH rate is currently `1.05e18` (rsETH has accrued 5% yield). The L2 `CrossChainRateReceiver.rate` is `1.00e18` (stale — not updated for several days).
2. Attacker calls `RSETHPoolV3.deposit{value: 100 ether}("")` on L2.
3. `viewSwapRsETHAmountAndFee(100 ether)` computes:
   - `fee = 100e18 * feeBps / 10_000` (e.g., 0 if feeBps=0 for simplicity)
   - `rsETHAmount = 100e18 * 1e18 / 1.00e18 = 100 rsETH`
4. At the true L1 rate of `1.05e18`, the attacker should have received `100e18 * 1e18 / 1.05e18 ≈ 95.24 rsETH`.
5. The attacker receives `100 rsETH` instead of `95.24 rsETH` — an excess of `~4.76 rsETH` minted against no additional ETH backing.
6. When the rate is subsequently updated to `1.05e18`, the protocol's per-token ETH value drops for all existing holders, as the total rsETH supply is now inflated relative to TVL. [10](#0-9) [11](#0-10)

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L13-16)
```text
    uint256 public rate;

    /// @notice Last time rate was updated
    uint256 public lastUpdated;
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L95-105)
```text
        rate = _rate;

        lastUpdated = block.timestamp;

        emit RateUpdated(_rate);
    }

    /// @notice Gets the last stored rate in the contract
    function getRate() external view returns (uint256) {
        return rate;
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

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L281-285)
```text
        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L422-426)
```text
        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L108-113)
```text
    function updateRate() external payable nonReentrant {
        uint256 latestRate = getLatestRate();

        rate = latestRate;

        lastUpdated = block.timestamp;
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L30-32)
```text
        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();
```

**File:** contracts/LRTDepositPool.sol (L76-92)
```text
    function depositETH(
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        payable
        nonReentrant
        whenNotPaused
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
```
