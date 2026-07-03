### Title
Stale Cross-Chain Rate in L2 Pools Allows Depositors to Mint Excess rsETH at a Discount — (File: contracts/cross-chain/CrossChainRateReceiver.sol)

---

### Summary

The `CrossChainRateReceiver` stores the rsETH/ETH exchange rate that is updated asynchronously via LayerZero messages from L1. The stored `rate` has no staleness check enforced at the point of use. L2 deposit pools (`RSETHPoolV3`, `RSETHPoolNoWrapper`) consume this rate directly to calculate how many rsETH tokens to mint for a depositor. When the L1 rsETH price has risen but the L2 rate has not yet been updated, a depositor can exploit the stale (lower) rate to receive more rsETH than the current L1 price entitles them to, diluting existing rsETH holders.

---

### Finding Description

`CrossChainRateReceiver` receives the rsETH/ETH rate from L1 via `lzReceive()` and stores it in the `rate` state variable along with a `lastUpdated` timestamp:

```solidity
// contracts/cross-chain/CrossChainRateReceiver.sol
rate = _rate;
lastUpdated = block.timestamp;
```

However, `lastUpdated` is **never validated** against any maximum staleness threshold anywhere in the codebase. The L2 pools call `getRate()` which simply returns the stored `rate` with no freshness check:

```solidity
// contracts/cross-chain/CrossChainRateReceiver.sol
function getRate() external view returns (uint256) {
    return rate;
}
```

`RSETHPoolV3.deposit()` and `RSETHPoolNoWrapper.deposit()` both call `viewSwapRsETHAmountAndFee()`, which divides by this potentially stale rate:

```solidity
// contracts/pools/RSETHPoolV3.sol
uint256 rsETHToETHrate = getRate();
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

The analog to the external report's vulnerability is direct: in the original finding, `importScore()` could be called at any time, allowing a worker to restore a previously high score after deliberately losing it. Here, `deposit()` can be called at any time using a previously recorded (stale) rate. The rate is updated asynchronously — only when a LayerZero message arrives from L1 — and there is no mechanism forcing synchronization at the time of a user's first or any subsequent interaction. A depositor can strategically time their deposit to exploit the window between a real L1 price increase and the L2 rate update.

---

### Impact Explanation

When the rsETH price on L1 increases (rsETH becomes worth more ETH), but the L2 `rate` has not yet been updated:

- `rsETHAmount = amountAfterFee * 1e18 / staleRate` yields **more rsETH** than `amountAfterFee * 1e18 / currentRate`
- The attacker receives rsETH representing a claim on more ETH than they deposited
- This excess rsETH can be bridged to L1 and redeemed, extracting value from the protocol's TVL
- Existing rsETH holders are diluted: the same pool of underlying assets now backs more rsETH tokens

**Impact: High — Theft of unclaimed yield / share mis-accounting.** The excess rsETH minted at the stale rate represents yield that belongs to existing rsETH holders, transferred to the attacker.

---

### Likelihood Explanation

The rate update depends on an off-chain keeper or bot sending a LayerZero message from L1 to L2. Any delay — due to network congestion, keeper downtime, or deliberate inaction — creates a window. Since rsETH accrues restaking rewards continuously, the L1 price rises over time, making the L2 rate perpetually slightly stale between updates. An attacker monitoring both L1 oracle updates and L2 rate updates can reliably identify and exploit these windows. No special permissions are required; any depositor can call `deposit()`.

---

### Recommendation

Enforce a maximum staleness threshold in the L2 pool contracts before accepting the rate for minting calculations. For example, in `RSETHPoolV3` and `RSETHPoolNoWrapper`, check that `block.timestamp - IRateReceiver(rsETHOracle).lastUpdated() <= MAX_RATE_AGE` before proceeding with the deposit. Alternatively, expose `lastUpdated` through the oracle interface and revert if the rate is stale. The `lastUpdated` field already exists in `CrossChainRateReceiver` but is never consumed by any caller.

---

### Proof of Concept

1. At time T, L1 rsETH price = 1.05 ETH. L2 `rate` = 1.05e18 (in sync).
2. L1 price rises to 1.10 ETH due to accrued restaking rewards. L2 `rate` remains 1.05e18 (stale).
3. Attacker calls `RSETHPoolV3.deposit{value: 100 ether}("ref")`.
4. `viewSwapRsETHAmountAndFee(100 ether)` computes: `rsETHAmount = 100e18 * 1e18 / 1.05e18 ≈ 95.24 rsETH`.
5. At the correct rate of 1.10e18, the attacker should receive: `100e18 * 1e18 / 1.10e18 ≈ 90.91 rsETH`.
6. Attacker receives ≈ 4.33 excess rsETH (≈ 4.76 ETH of value at the current rate).
7. Attacker bridges the excess rsETH to L1 via the wrapper and redeems it, extracting ETH from the protocol at the expense of existing rsETH holders. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L13-17)
```text
    uint256 public rate;

    /// @notice Last time rate was updated
    uint256 public lastUpdated;

```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L93-100)
```text
        uint256 _rate = abi.decode(_payload, (uint256));

        rate = _rate;

        lastUpdated = block.timestamp;

        emit RateUpdated(_rate);
    }
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L102-105)
```text
    /// @notice Gets the last stored rate in the contract
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L246-265)
```text
    function deposit(string memory referralId)
        external
        payable
        nonReentrant
        whenNotPaused
        limitDailyMint(msg.value, ETH_IDENTIFIER)
    {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
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
