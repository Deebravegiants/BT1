### Title
Stale Oracle Rate in `AGETHPoolV3` Allows Excess agETH Minting, Diluting Existing Holders — (`contracts/agETH/AGETHPoolV3.sol`)

---

### Summary

`AGETHPoolV3.deposit()` mints agETH using a rate fetched from `AGETHRateReceiver` (a `CrossChainRateReceiver`). The receiver stores `lastUpdated` but **never checks it** in `getRate()`. If the LayerZero message delivering the updated rate is delayed, the stale-low rate causes `viewSwapAgETHAmountAndFee` to mint more agETH than the deposited ETH warrants, diluting existing holders' yield.

---

### Finding Description

`CrossChainRateReceiver.getRate()` returns the raw stored `rate` with no freshness guard: [1](#0-0) 

`lastUpdated` is written on every `lzReceive` call but is never read by `getRate()`: [2](#0-1) [3](#0-2) 

`AGETHPoolV3.getRate()` blindly proxies to the oracle: [4](#0-3) 

`viewSwapAgETHAmountAndFee` uses the rate directly in the mint calculation with no staleness check: [5](#0-4) 

`deposit(string)` calls this and mints the resulting amount unconditionally: [6](#0-5) 

---

### Impact Explanation

The agETH-to-ETH rate is monotonically increasing (it represents accumulated staking yield). If the stored rate is stale-low — say `1.05e18` when the true rate is `1.10e18` — the mint formula `amountAfterFee * 1e18 / staleRate` produces more agETH than the deposited ETH backs at the current rate. The excess agETH dilutes the ETH-per-agETH ratio for all existing holders, effectively transferring their unclaimed yield to the attacker. This matches the scoped impact: **High — Theft of unclaimed yield**.

---

### Likelihood Explanation

LayerZero message delays are a realistic, non-adversarial operational condition (network congestion, bridge downtime, sequencer issues). An attacker only needs to:
1. Monitor the on-chain `rate` vs. the true rate on the source chain.
2. Deposit ETH during the staleness window.

No privileged access, key compromise, or governance capture is required. The attacker is an unprivileged EOA calling a public `payable` function.

---

### Recommendation

Add a staleness check in `CrossChainRateReceiver.getRate()` using `lastUpdated`:

```solidity
uint256 public constant MAX_RATE_AGE = 24 hours; // configurable

function getRate() external view returns (uint256) {
    require(block.timestamp - lastUpdated <= MAX_RATE_AGE, "Rate is stale");
    return rate;
}
```

Alternatively, enforce the check inside `AGETHPoolV3.viewSwapAgETHAmountAndFee` by reading `lastUpdated` directly from the oracle interface and reverting if the rate is too old.

---

### Proof of Concept

```solidity
// Fork test (local fork, unmodified contracts)
// 1. Deploy AGETHRateReceiver; set rate = 1.05e18, lastUpdated = block.timestamp - 2 days
// 2. Deploy AGETHPoolV3 pointing to that receiver
// 3. Record existing holder's agETH balance and ETH backing
// 4. Attacker calls deposit{value: 1 ether}("")
//    => agETHAmount = 1e18 * 1e18 / 1.05e18 ≈ 0.952 agETH
//    (at true rate 1.10e18 it should be ≈ 0.909 agETH — attacker gets ~4.7% excess)
// 5. Assert: attacker's agETH * trueRate / 1e18 > 1 ether  (more ETH value than deposited)
// 6. Assert: existing holder's ETH-per-agETH ratio has decreased (dilution confirmed)
``` [7](#0-6) [1](#0-0)

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L17-17)
```text

```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L97-97)
```text
        lastUpdated = block.timestamp;
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L103-105)
```text
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/agETH/AGETHPoolV3.sol (L104-106)
```text
    function getRate() public view returns (uint256) {
        return IOracle(agETHOracle).getRate();
    }
```

**File:** contracts/agETH/AGETHPoolV3.sol (L115-128)
```text
    function deposit(string memory referralId) external payable nonReentrant {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 agETHAmount, uint256 fee) = viewSwapAgETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        agETH.mint(msg.sender, agETHAmount);

        emit SwapOccurred(msg.sender, agETHAmount, fee, referralId);
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
