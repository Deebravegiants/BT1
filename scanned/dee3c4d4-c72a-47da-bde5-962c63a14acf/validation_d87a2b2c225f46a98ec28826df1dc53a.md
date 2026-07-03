Now I have all the information needed to make a determination. Let me trace the full attack path through the production code.

### Title
Missing Staleness Check in `CrossChainRateReceiver.getRate()` Allows Inflated rsETH Extraction from `RSETHPoolNoWrapper` — (`contracts/pools/RSETHPoolNoWrapper.sol`)

---

### Summary

`CrossChainRateReceiver` stores a `lastUpdated` timestamp when a rate is received via LayerZero, but `getRate()` returns the cached `rate` unconditionally without ever validating freshness. `RSETHPoolNoWrapper.deposit()` calls this oracle and transfers rsETH from its own pre-funded balance at the stale rate. When the rate is stale-low, every depositor receives more rsETH than their ETH is worth, draining the pool's rsETH reserves. The ETH bridged to L1 mints only the fair-value rsETH amount, so the pool can never be fully replenished, and future depositors are permanently shortchanged.

---

### Finding Description

`CrossChainRateReceiver` records `lastUpdated = block.timestamp` each time a LayerZero message arrives, but `getRate()` simply returns `rate` with no age check:

```solidity
// CrossChainRateReceiver.sol line 97
lastUpdated = block.timestamp;   // stored but never validated

// line 103-105
function getRate() external view returns (uint256) {
    return rate;                 // no staleness guard
}
``` [1](#0-0) 

`RSETHPoolNoWrapper.deposit()` calls `viewSwapRsETHAmountAndFee()`, which divides by this unchecked rate:

```solidity
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
``` [2](#0-1) 

The result is immediately transferred from the pool's own rsETH balance with no slippage floor and no minimum-amount parameter:

```solidity
rsETH.safeTransfer(msg.sender, rsETHAmount);
``` [3](#0-2) 

The pool is a **transfer-based** pool (not a mint-based one). It holds a finite rsETH balance that is replenished only after the collected ETH is bridged to L1 and the L1Vault mints rsETH at the true rate. If the oracle is stale-low, the attacker extracts more rsETH than the ETH they deposited is worth; the subsequent L1 replenishment mints only the fair-value amount, leaving a permanent deficit.

`InterimRSETHOracle` (the alternative oracle implementation) has the same issue — `getRate()` returns `rate` with no freshness check: [4](#0-3) 

`ChainlinkOracleForRSETHPoolCollateral` checks `answeredInRound < roundID` but has no heartbeat/max-age guard, so a Chainlink feed that stops updating (while still returning the last round) is also exploitable: [5](#0-4) 

---

### Impact Explanation

**High — Theft of unclaimed yield.**

The excess rsETH extracted by the attacker represents yield that was pre-funded into the pool for future depositors. Because the L1 replenishment is proportional to the ETH deposited (at the true rate), the pool's rsETH balance after replenishment is permanently lower than it should be. Remaining depositors receive less rsETH than they are owed, or `safeTransfer` reverts entirely once the balance is exhausted, freezing their yield.

---

### Likelihood Explanation

LayerZero cross-chain message delivery is subject to real-world delays (network congestion, relayer downtime, bridge pauses). A stale rate requires no oracle operator compromise — it is a natural failure mode of the push-based oracle architecture. An attacker can monitor `lastUpdated` on-chain and act as soon as the rate drifts below the true value. The attack is permissionless, requires only ETH, and is executable in a single transaction.

---

### Recommendation

1. **Add a staleness guard in `CrossChainRateReceiver.getRate()`:**
   ```solidity
   uint256 public constant MAX_RATE_AGE = 24 hours;

   function getRate() external view returns (uint256) {
       require(block.timestamp - lastUpdated <= MAX_RATE_AGE, "Stale rate");
       return rate;
   }
   ```
2. **Add a heartbeat check in `ChainlinkOracleForRSETHPoolCollateral.getRate()`:**
   ```solidity
   require(block.timestamp - timestamp <= MAX_ORACLE_AGE, "Stale price");
   ```
3. **Add a `minRsETHAmount` slippage parameter to `RSETHPoolNoWrapper.deposit()`** so depositors cannot be front-run and the pool cannot silently over-distribute.
4. **Consider a circuit-breaker** in `RSETHPoolNoWrapper` that pauses deposits when `block.timestamp - IOracle(rsETHOracle).lastUpdated() > threshold`.

---

### Proof of Concept

```solidity
// Fork test (Unichain fork, unmodified contracts)
// 1. Deploy MockStaleOracle returning 0.5e18 (50% of true ~1.05e18 rate)
// 2. Admin calls rsETHPoolNoWrapper.setRSETHOracle(mockStaleOracle)  [TIMELOCK_ROLE]
//    -- OR -- simply wait for CrossChainRateReceiver to go stale naturally
// 3. Attacker deposits 100 ETH:
//    rsETHAmount = 100e18 * 1e18 / 0.5e18 = 200e18 rsETH  (fair value ≈ 95.2e18)
// 4. Assert: attacker received 200e18 rsETH vs fair 95.2e18 rsETH
// 5. Assert: pool rsETH balance < amount needed for next honest depositor
// 6. Next depositor's deposit() reverts (ERC20 insufficient balance)
// 7. ETH bridged to L1 mints only ~95.2e18 rsETH — pool deficit is permanent
```

The `lastUpdated` field is publicly readable on `CrossChainRateReceiver`, so an attacker can trivially detect staleness without any privileged access. [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L16-17)
```text
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

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L231-244)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        rsETH.safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
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

**File:** contracts/pools/oracle/InterimRSETHOracle.sol (L49-51)
```text
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L26-37)
```text
    function getRate() public view returns (uint256) {
        (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
            AggregatorV3Interface(oracle).latestRoundData();

        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();

        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());

        return normalizedPrice;
    }
```
