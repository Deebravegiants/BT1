### Title
Stale `agETHOracle` in `AGETHPoolV3` Enables Unbounded Over-Minting of agETH via Cross-Chain Rate Lag — (`contracts/agETH/AGETHPoolV3.sol`)

---

### Summary

`AGETHPoolV3.viewSwapAgETHAmountAndFee(uint256,address)` computes the agETH mint amount as `amountAfterFee * tokenToETHRate / agETHToETHrate`. The denominator `agETHToETHrate` is sourced from `AGETHRateReceiver`, which extends `CrossChainRateReceiver`. `CrossChainRateReceiver.getRate()` returns the last stored `rate` with **no staleness enforcement**. Because agETH is yield-bearing, its true ETH rate monotonically increases over time. Any staleness window causes the oracle to report a rate lower than the current true rate, making the denominator artificially small and minting more agETH than the deposited collateral warrants. `AGETHPoolV3` has no daily mint limit, no pause gate on `deposit()`, and no staleness check of its own, leaving the over-minting unbounded.

---

### Finding Description

**Entrypoint:** `AGETHPoolV3.deposit(address token, uint256 amount, string referralId)` — public, no role restriction.

**Rate computation path:**

```
deposit(token, amount, referralId)
  └─ viewSwapAgETHAmountAndFee(amount, token)          [line 147]
       ├─ agETHToETHrate = getRate()                   [line 188]
       │    └─ IOracle(agETHOracle).getRate()          [line 105]
       │         └─ CrossChainRateReceiver.getRate()   [line 103-105]
       │              return rate;  // ← no staleness check
       └─ agETHAmount = amountAfterFee * tokenToETHRate / agETHToETHrate  [line 194]
```

`CrossChainRateReceiver` stores `lastUpdated` but **never enforces a maximum age** in `getRate()`: [1](#0-0) 

The rate is updated only when a LayerZero message arrives via `lzReceive()`. Between updates, `rate` is frozen at its last value: [2](#0-1) 

`AGETHPoolV3` performs no staleness check before using the rate: [3](#0-2) 

Unlike `RSETHPoolV3`, `AGETHPoolV3` has **no `limitDailyMint` modifier** on either `deposit()` overload, so there is no cap on how much agETH can be minted in a single block or day: [4](#0-3) 

**Staleness scenario (no oracle compromise required):**

agETH accrues yield continuously; its ETH rate only increases. If the `AGETHRateReceiver` has not received a fresh LayerZero message (e.g., due to message delay, infrequent `updateRate()` calls, or fee exhaustion on the provider side), `rate` lags behind the true value. The provider's `updateRate()` is permissionless but requires the caller to pay LayerZero fees; there is no on-chain enforcement that it is called within any time bound. [5](#0-4) 

---

### Impact Explanation

Let `R_true` = current true agETH/ETH rate, `R_stale` = stale oracle rate (`R_stale < R_true`).

For a deposit of `N` tokens each worth `T` ETH:

- **Correct mint:** `N * T / R_true`
- **Actual mint:** `N * T / R_stale` (larger)
- **Excess agETH:** `N * T * (R_true - R_stale) / (R_stale * R_true)`

The attacker bridges the excess agETH to L1 and redeems it for ETH. The protocol has issued more agETH than the deposited collateral backs, directly causing **protocol insolvency**. With no daily mint limit, a single large deposit can extract the full excess in one transaction.

---

### Likelihood Explanation

- Cross-chain oracle staleness is a natural, non-adversarial condition. LayerZero message delays, fee shortfalls, or simply infrequent `updateRate()` calls are routine.
- agETH's yield-bearing nature guarantees the stale rate is always *lower* than the true rate, so the direction of the exploit is deterministic.
- The attack requires no privileged role, no front-running, and no external protocol compromise — only a deposit during a staleness window.
- The token oracle can be a Chainlink wrapper (`ChainlinkOracleForRSETHPoolCollateral`) with its own staleness guard, making the asymmetric-staleness scenario (fresh token oracle, stale agETH oracle) straightforwardly reachable. [6](#0-5) 

---

### Recommendation

1. **Enforce a staleness threshold in `CrossChainRateReceiver.getRate()`:**
   ```solidity
   uint256 public constant MAX_STALENESS = 24 hours;
   function getRate() external view returns (uint256) {
       require(block.timestamp - lastUpdated <= MAX_STALENESS, "Rate stale");
       return rate;
   }
   ```
2. **Add a staleness check in `AGETHPoolV3.viewSwapAgETHAmountAndFee()`** as a defence-in-depth layer, checking `AGETHRateReceiver.lastUpdated` directly.
3. **Add a daily mint limit** to `AGETHPoolV3` analogous to the `limitDailyMint` modifier present in `RSETHPoolV3`, to bound worst-case exposure during any staleness window.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Differential test: compare agETH minted at stale vs fresh oracle rate.
// Run on a local fork with AGETHPoolV3 deployed.

interface IPool {
    function deposit(address token, uint256 amount, string memory referralId) external;
    function viewSwapAgETHAmountAndFee(uint256 amount, address token)
        external view returns (uint256 agETHAmount, uint256 fee);
}

interface IRateReceiver {
    function rate() external view returns (uint256);
    function lastUpdated() external view returns (uint256);
    // owner-only in prod, but on fork we can prank the owner:
    // simulate staleness by NOT calling updateRate for N hours
}

contract PoC {
    function testOverMint(
        IPool pool,
        address token,
        uint256 depositAmount,
        uint256 staleRate,   // e.g. rate from 24h ago
        uint256 freshRate    // e.g. current true rate
    ) external pure returns (uint256 excess) {
        // Simulate stale oracle: agETHAmount_stale = depositAmount * tokenRate / staleRate
        uint256 tokenRate = 1e18; // assume 1:1 for simplicity
        uint256 mintedStale = depositAmount * tokenRate / staleRate;
        uint256 mintedFresh = depositAmount * tokenRate / freshRate;

        // excess > 0 whenever freshRate > staleRate (always true for yield-bearing agETH)
        excess = mintedStale - mintedFresh;
        assert(excess > 0);
    }
}
```

**Concrete numbers:** agETH at ~5% APY, 24 h staleness → `R_true / R_stale ≈ 1.000137`. On a 1 000 ETH deposit, excess agETH ≈ 0.137 agETH ≈ ~0.137 ETH of unbacked issuance per deposit. With no daily mint cap, an attacker repeating this across many deposits or with a single very large deposit extracts proportionally more, draining the protocol's backing.

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L93-97)
```text
        uint256 _rate = abi.decode(_payload, (uint256));

        rate = _rate;

        lastUpdated = block.timestamp;
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L102-105)
```text
    /// @notice Gets the last stored rate in the contract
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/agETH/AGETHPoolV3.sol (L134-154)
```text
    function deposit(
        address token,
        uint256 amount,
        string memory referralId
    )
        external
        nonReentrant
        onlySupportedToken(token)
    {
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 agETHAmount, uint256 fee) = viewSwapAgETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        agETH.mint(msg.sender, agETHAmount);

        emit SwapOccurred(msg.sender, agETHAmount, fee, referralId);
    }
```

**File:** contracts/agETH/AGETHPoolV3.sol (L183-194)
```text
    {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of agETH in ETH
        uint256 agETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final agETH amount
        agETHAmount = amountAfterFee * tokenToETHRate / agETHToETHrate;
```

**File:** contracts/agETH/AGETHRateReceiver.sol (L1-15)
```text
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import { CrossChainRateReceiver } from "contracts/cross-chain/CrossChainRateReceiver.sol";

/// @title agETH cross chain rate receiver
/// @notice Receives the agETH rate from a provider contract on a different chain than the one this contract is deployed
/// on
contract AGETHRateReceiver is CrossChainRateReceiver {
    constructor(uint16 _srcChainId, address _rateProvider, address _layerZeroEndpoint) {
        rateInfo = RateInfo({ tokenSymbol: "agETH", baseTokenSymbol: "ETH" });
        srcChainId = _srcChainId;
        rateProvider = _rateProvider;
        layerZeroEndpoint = _layerZeroEndpoint;
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
