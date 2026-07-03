### Title
Stale Cross-Chain Rate Enables Over-Minting of wrsETH/agETH, Causing Protocol Insolvency — (`contracts/cross-chain/CrossChainRateReceiver.sol`)

---

### Summary

`CrossChainRateReceiver.getRate()` returns the last stored `rate` with no staleness check. The `lastUpdated` timestamp is recorded on every `lzReceive` call but is never validated by `getRate()` or by any downstream consumer (`RSETHPoolV2`, `RSETHPoolV3`, `AGETHPoolV3`). If the LayerZero bridge stops delivering updates while the L1 rsETH price appreciates, all three pools continue minting wrsETH/agETH at the outdated lower rate, issuing more shares than the deposited ETH can back at the true L1 rate.

---

### Finding Description

**Root cause — `CrossChainRateReceiver.getRate()` (lines 103–105):**

`lzReceive` correctly records `lastUpdated = block.timestamp` on every update, but `getRate()` ignores it entirely:

```solidity
// CrossChainRateReceiver.sol line 97
lastUpdated = block.timestamp;   // stored, never read again

// line 103-105
function getRate() external view returns (uint256) {
    return rate;                 // no staleness guard
}
``` [1](#0-0) 

**Downstream consumers — all three pools call `getRate()` unconditionally:**

`RSETHPoolV3.viewSwapRsETHAmountAndFee` (ETH path):
```solidity
uint256 rsETHToETHrate = getRate();
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
``` [2](#0-1) 

`RSETHPoolV3.viewSwapRsETHAmountAndFee` (token path):
```solidity
uint256 rsETHToETHrate = getRate();
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
``` [3](#0-2) 

`RSETHPoolV2.viewSwapRsETHAmountAndFee`:
```solidity
uint256 rsETHToETHrate = getRate();
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
``` [4](#0-3) 

`AGETHPoolV3.viewSwapAgETHAmountAndFee`:
```solidity
uint256 agETHToETHrate = getRate();
agETHAmount = amountAfterFee * 1e18 / agETHToETHrate;
``` [5](#0-4) 

None of these functions check `lastUpdated` before using the rate.

---

### Impact Explanation

rsETH is a yield-bearing token: its ETH-denominated rate (`rsETHToETHrate`) strictly increases over time. The mint formula is:

```
wrsETH_minted = ETH_deposited / rsETHToETHrate
```

If `rsETHToETHrate` is stale-low (e.g., `1.01e18` while the true L1 rate is `1.05e18`), the pool mints:

- **Stale rate:** `1e18 / 1.01e18 ≈ 0.9901 wrsETH` per ETH
- **True rate:** `1e18 / 1.05e18 ≈ 0.9524 wrsETH` per ETH

The pool over-mints **≈ 3.9% more wrsETH** per ETH deposited. The ETH collected is bridged to L1 and converted to rsETH at the true rate, yielding only `0.9524 rsETH`. The `0.9901 wrsETH` outstanding cannot be fully redeemed — the backing rsETH is insufficient. Over a 30-day staleness window with realistic rsETH appreciation, the shortfall compounds across all deposits made during that window, constituting **protocol insolvency**.

The `dailyMintLimit` caps per-day exposure but does not prevent the insolvency from accumulating day-by-day across the entire staleness window. [6](#0-5) 

---

### Likelihood Explanation

LayerZero bridge outages and message delivery failures are documented, real-world events. The protocol has no circuit-breaker that pauses deposits when `lastUpdated` is too old. Any bridge interruption lasting more than a few hours while rsETH accrues yield is sufficient to trigger the condition. No attacker action is required — ordinary users depositing during the outage are the unwitting source of the insolvency.

---

### Recommendation

Add a configurable `maxStaleness` threshold and revert in `getRate()` if the rate is too old:

```solidity
uint256 public maxStaleness; // e.g., 24 hours

function getRate() external view returns (uint256) {
    require(block.timestamp - lastUpdated <= maxStaleness, "Rate is stale");
    return rate;
}
```

Alternatively, expose `lastUpdated` and enforce the check in each pool's `viewSwapRsETHAmountAndFee` / `viewSwapAgETHAmountAndFee` before computing the mint amount.

---

### Proof of Concept

```solidity
// Fork test (local fork, no public mainnet)
function testStaleRateCausesOverMint() public {
    // 1. Simulate one LZ update at rate = 1.01e18
    vm.prank(layerZeroEndpoint);
    receiver.lzReceive(srcChainId, abi.encodePacked(rateProvider), 0,
                       abi.encode(uint256(1.01e18)));

    // 2. Warp 30 days — bridge goes silent, true L1 rate is now ~1.05e18
    vm.warp(block.timestamp + 30 days);

    // 3. User deposits 1 ETH into RSETHPoolV3
    uint256 deposit = 1 ether;
    (uint256 wrsETHMinted,) = pool.viewSwapRsETHAmountAndFee(deposit);

    // 4. wrsETHMinted uses stale 1.01e18 → ~0.9901e18
    // true backing at 1.05e18 → ~0.9524e18
    uint256 trueRsETHBacking = deposit * 1e18 / 1.05e18;
    assertGt(wrsETHMinted, trueRsETHBacking);
    // wrsETHMinted ≈ 0.9901e18 > trueRsETHBacking ≈ 0.9524e18 → PASS
    // Protocol is undercollateralized by ~3.9% per deposited ETH
}
```

### Citations

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

**File:** contracts/pools/RSETHPoolV3.sol (L96-125)
```text
    modifier limitDailyMint(uint256 amount, address token) {
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
        }

        uint256 rsETHAmount;

        // Calculate the amount of rsETH that will be minted
        if (token == ETH_IDENTIFIER) {
            (rsETHAmount,) = viewSwapRsETHAmountAndFee(amount);
        } else {
            (rsETHAmount,) = viewSwapRsETHAmountAndFee(amount, token);
        }

        uint256 currentDay = getCurrentDay();

        // If the current day is greater than the last mint day, reset the daily mint amount
        if (currentDay > lastMintDay) {
            lastMintDay = currentDay;
            dailyMintAmount = 0;
        }

        // Check if the daily mint amount plus the amount to mint is greater than the daily mint limit
        if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
            revert DailyMintLimitExceeded();
        }

        dailyMintAmount += rsETHAmount;
        _;
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

**File:** contracts/pools/RSETHPoolV3.sol (L315-335)
```text
    function viewSwapRsETHAmountAndFee(
        uint256 amount,
        address token
    )
        public
        view
        onlySupportedToken(token)
        returns (uint256 rsETHAmount, uint256 fee)
    {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
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

**File:** contracts/agETH/AGETHPoolV3.sol (L160-169)
```text
    function viewSwapAgETHAmountAndFee(uint256 amount) public view returns (uint256 agETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of agETH in ETH
        uint256 agETHToETHrate = getRate();

        // Calculate the final agETH amount
        agETHAmount = amountAfterFee * 1e18 / agETHToETHrate;
    }
```
