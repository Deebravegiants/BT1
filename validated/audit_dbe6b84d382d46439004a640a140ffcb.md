### Title
Publicly Callable `updateRSETHPrice()` Enables Sandwich Attack to Steal Yield from rsETH Holders - (File: contracts/LRTOracle.sol)

---

### Summary

`LRTOracle.updateRSETHPrice()` carries no access control — any address can call it. The L1 deposit pool mints rsETH using the **stored** (potentially stale) `rsETHPrice` rather than the live TVL-derived price. An attacker can atomically: (1) deposit at the stale lower price to receive excess rsETH, (2) trigger the price update, and (3) sell the excess rsETH on a secondary market, extracting yield that belongs to existing rsETH holders.

---

### Finding Description

**Root cause — `updateRSETHPrice()` is permissionlessly callable:** [1](#0-0) 

The function carries only a `whenNotPaused` guard; any EOA or contract may call it at will.

**Root cause — deposit minting uses the stored stale price:** [2](#0-1) 

`lrtOracle.rsETHPrice()` returns the last **written** value of the storage variable, not a freshly computed one. The deposit function never calls `updateRSETHPrice()` before computing the mint amount.

**How the price becomes stale:**

Rewards accrue continuously in EigenLayer strategies. `_getTotalEthInProtocol()` sums the current on-chain balances, so `totalETHInProtocol` grows over time. The stored `rsETHPrice` only advances when `_updateRsETHPrice()` is executed. [3](#0-2) 

Between two consecutive calls to `updateRSETHPrice()`, the stored price is lower than the fair price (`totalETHInProtocol / rsethSupply`). Any deposit during this window mints more rsETH than the depositor is entitled to.

**Fee minting compounds the issue:**

When `updateRSETHPrice()` is finally called, the protocol computes `previousTVL = rsethSupply * rsETHPrice` using the stale price. Because the attacker's deposit inflated `rsethSupply` while the stale price was still in effect, `previousTVL` is understated, `rewardAmount` is overstated, and the treasury receives an inflated fee mint — further diluting honest holders. [4](#0-3) 

---

### Impact Explanation

Existing rsETH holders suffer dilution: the attacker receives rsETH at a below-fair-value price, reducing the ETH backing per rsETH for everyone else. The attacker can immediately liquidate the excess rsETH on any secondary market (Curve, Uniswap, etc.) without waiting for the 8-day L1 withdrawal delay. This constitutes **theft of unclaimed yield** from honest depositors.

**Impact: High** — theft of unclaimed yield.

---

### Likelihood Explanation

- `updateRSETHPrice()` is not called atomically inside deposits; any gap between keeper invocations creates a window.
- Keeper failures, gas spikes, or deliberate delay by the attacker (who can simply refrain from calling the function until a profitable gap opens) all create exploitable staleness.
- The `pricePercentageLimit` check only blocks non-manager callers when the price increase exceeds the configured threshold; small daily accruals (e.g., 0.05 % per day) pass freely. [5](#0-4) 

**Likelihood: Medium.**

---

### Recommendation

1. **Call `updateRSETHPrice()` inside `_beforeDeposit`** (or inside `getRsETHAmountToMint`) so the mint calculation always uses a fresh price.
2. **Alternatively**, restrict `updateRSETHPrice()` to a keeper role and ensure the keeper is called atomically with deposits, or use a TWAP / time-weighted price to smooth out stale-price arbitrage.

---

### Proof of Concept

**Setup:**
- TVL = 1 100 ETH (100 ETH rewards have accrued since last update)
- rsETH supply = 1 000
- Stored `rsETHPrice` = 1.00 ETH (stale)
- Fair price = 1 100 / 1 000 = **1.10 ETH**

**Step 1 — Attacker deposits 100 ETH at stale price:**

```
rsethAmountToMint = (100 ETH × 1e18) / 1.00e18 = 100 rsETH
```

Fair amount would be `100 / 1.10 ≈ 90.9 rsETH`. Attacker receives **9.1 excess rsETH**.

**Step 2 — Attacker calls `updateRSETHPrice()`:**

```
totalETHInProtocol = 1 200 ETH   (1 100 + 100 deposited)
rsethSupply        = 1 100
newRsETHPrice      = 1 200 / 1 100 ≈ 1.0909 ETH
```

**Step 3 — Attacker sells 100 rsETH on a DEX at ≈ 1.0909 ETH:**

```
Proceeds  = 100 × 1.0909 ≈ 109.09 ETH
Cost      = 100 ETH
Profit    ≈ 9.09 ETH
```

Existing holders (1 000 rsETH) now hold claims worth `1 000 × 1.0909 = 1 090.9 ETH` instead of the `1 100 ETH` they were entitled to before the attacker's deposit — a loss of **≈ 9.1 ETH** transferred to the attacker.

The entry path is fully permissionless:
- `LRTDepositPool.depositETH()` → `_beforeDeposit()` → `getRsETHAmountToMint()` → reads stale `rsETHPrice`
- `LRTOracle.updateRSETHPrice()` → callable by anyone [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/LRTOracle.sol (L85-89)
```text
    /// @notice updates RSETH/ETH exchange rate
    /// @dev calculates rsETH price based on stakedAsset value received from EigenLayer
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L230-250)
```text
        // get total ETH in the protocol (normalized to 1e18)
        uint256 totalETHInProtocol = _getTotalEthInProtocol();

        // calculate previousTVL using rsethSupply multiplied by rsETHPrice
        uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);

        IPausable lrtDepositPool = IPausable(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable withdrawalManager = IPausable(lrtConfig.getContract(LRTConstants.LRT_WITHDRAW_MANAGER));

        // determine if the protocol is active (not paused)
        bool protocolPaused = lrtDepositPool.paused() || withdrawalManager.paused() || paused;

        // only take fee if TVL increased and protocol is not paused
        uint256 protocolFeeInETH = 0;
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L252-266)
```text
        if (newRsETHPrice > highestRsethPrice) {
            // check if the price is above the threshold
            uint256 priceDifference = newRsETHPrice - highestRsethPrice;
            // pricePercentageLimit is in 1e18 precision (100% = 1e18, 1% = 1e16)
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);

            // check if the price difference is above the threshold
            if (isPriceIncreaseOffLimit) {
                // if sender has a manager role, this doesn't revert.
                // if not, it reverts as price went above the threshold
                if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
                    revert PriceAboveDailyThreshold();
                }
            }
```

**File:** contracts/LRTDepositPool.sol (L76-93)
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
    }
```

**File:** contracts/LRTDepositPool.sol (L515-521)
```text
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```
