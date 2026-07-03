### Title
Stale Cross-Chain Rate in `CrossChainRateReceiver.getRate()` Enables Over-Minting of wrsETH/rsETH on L2 Pools - (File: contracts/cross-chain/CrossChainRateReceiver.sol)

---

### Summary

`CrossChainRateReceiver.getRate()` returns the stored `rate` with no staleness check against `lastUpdated`. All L2 deposit pools consume this rate to compute how many wrsETH/rsETH tokens to mint per unit of ETH or LST deposited. When the stored rate is stale and lower than the true current rsETH/ETH exchange rate, the division `amountAfterFee * 1e18 / rsETHToETHrate` yields a larger token amount than the deposit warrants, allowing any depositor to extract more value than they put in.

---

### Finding Description

`CrossChainRateReceiver` stores two state variables: `rate` (the last pushed rsETH/ETH exchange rate) and `lastUpdated` (the timestamp of that push). The `getRate()` view function returns `rate` unconditionally:

```solidity
// CrossChainRateReceiver.sol lines 103-105
function getRate() external view returns (uint256) {
    return rate;
}
```

`lastUpdated` is recorded on every `lzReceive` call but is never consulted by `getRate()`. There is no maximum-age guard, no circuit-breaker, and no revert path for a stale value.

Every L2 pool variant calls this oracle directly:

- `RSETHPoolV3.viewSwapRsETHAmountAndFee` (ETH path, line 304): `uint256 rsETHToETHrate = getRate();`
- `RSETHPoolV3.viewSwapRsETHAmountAndFee` (token path, line 328): same call
- `RSETHPoolV3ExternalBridge.viewSwapRsETHAmountAndFee` (lines 423, 446): same call
- `RSETHPoolNoWrapper.viewSwapRsETHAmountAndFee` (lines 282, 305): same call

The mint formula in all three pools is:

```
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate   // ETH path
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate  // LST path
```

A stale (lower-than-actual) `rsETHToETHrate` inflates `rsETHAmount`. The attacker deposits at the stale rate, receives excess wrsETH/rsETH, and redeems it after the rate is corrected, extracting more ETH than was deposited.

The rate is pushed from L1 via LayerZero through `MultiChainRateProvider.updateRate()` (callable by anyone, no access control) or `CrossChainRateProvider.updateRate()`. LayerZero message delivery is not instantaneous and can be delayed by minutes to hours under congestion. rsETH accrues staking rewards continuously; even a 1-hour delay at typical staking yields (~4% APY) produces a ~0.0046% rate discrepancy. Over large deposit volumes this is directly profitable.

---

### Impact Explanation

**Critical — Direct theft of user funds.**

An attacker who deposits N ETH when the oracle rate is stale by δ receives `N / (rate - δ)` wrsETH instead of the correct `N / rate`. On redemption at the corrected rate, they recover `(N / (rate - δ)) * rate` ETH > N ETH. The surplus is drawn from the pool's ETH balance, which is funded by other depositors. The `RSETHPoolNoWrapper` variant transfers pre-minted rsETH directly from pool reserves, making the drain immediate and concrete.

---

### Likelihood Explanation

**Medium.**

LayerZero cross-chain messages are not guaranteed to arrive within any fixed window. Network congestion, gas price spikes on the destination chain, or simply no one calling `updateRate()` for an extended period all produce a stale rate. rsETH appreciates monotonically (staking rewards), so the rate is always drifting upward between updates. An attacker needs only to monitor `CrossChainRateReceiver.lastUpdated` on-chain and deposit when the gap is large enough to be profitable after fees. No privileged access, no oracle compromise, and no external protocol manipulation is required.

---

### Recommendation

Add a staleness guard in `CrossChainRateReceiver.getRate()`:

```solidity
uint256 public constant MAX_RATE_AGE = 24 hours; // configurable

function getRate() external view returns (uint256) {
    require(block.timestamp - lastUpdated <= MAX_RATE_AGE, "Rate is stale");
    return rate;
}
```

Alternatively, revert in the pool's `viewSwapRsETHAmountAndFee` if the oracle's `lastUpdated` is too old. The pool contracts should also expose the oracle's `lastUpdated` so off-chain monitors can alert before the window expires.

---

### Proof of Concept

1. Observe `CrossChainRateReceiver.lastUpdated` on the target L2. Suppose the last update was 6 hours ago and the true L1 rsETH price has risen from 1.0400 ETH to 1.0405 ETH (normal staking accrual).

2. The stale `rate` stored in `CrossChainRateReceiver` is still `1.0400e18`.

3. Attacker calls `RSETHPoolNoWrapper.deposit{value: 1000 ether}("")`:
   - `viewSwapRsETHAmountAndFee(1000e18)` computes `rsETHAmount = 1000e18 * 1e18 / 1.0400e18 = 961.538...e18`
   - Pool transfers `961.538 rsETH` to attacker.

4. Correct amount at true rate: `1000e18 * 1e18 / 1.0405e18 = 961.076...e18`.

5. Attacker holds `961.538 rsETH`. After the rate is updated on L2 (or attacker bridges to L1), they redeem `961.538 rsETH` for `961.538 * 1.0405 = 1000.46 ETH`.

6. Net profit: `~0.46 ETH` on a 1000 ETH deposit (0.046%). Scaled to the pool's TVL (tens of millions of ETH), this is a material theft per stale window.

**Root cause line references:** [1](#0-0) 

`lastUpdated` is written but never read in `getRate()`: [2](#0-1) 

Pool consumes the unchecked rate directly: [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

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
