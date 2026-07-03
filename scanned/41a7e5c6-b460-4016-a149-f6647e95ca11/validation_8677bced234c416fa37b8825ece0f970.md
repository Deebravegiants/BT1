### Title
Stale Manually Updated rsETH/ETH Rate in `InterimRSETHOracle` Allows Depositors to Extract Excess rsETH from L2 Pools - (File: contracts/pools/oracle/InterimRSETHOracle.sol)

---

### Summary

`InterimRSETHOracle` stores a manually set rsETH/ETH exchange rate with no staleness tracking, no timestamp, and no upper-bound protection. Every L2 pool contract (`RSETHPool`, `RSETHPoolV2`, `RSETHPoolV3`, `RSETHPoolNoWrapper`, and their bridge variants) reads this rate to compute how many rsETH tokens to issue per ETH deposited. Because rsETH naturally appreciates over time as L1 staking rewards accrue, any lag between the true rate and the stored rate creates a window where any depositor can receive more rsETH than the ETH they provide is worth, extracting value from existing rsETH holders.

---

### Finding Description

`InterimRSETHOracle` is a production contract in `contracts/pools/oracle/InterimRSETHOracle.sol`. Its only validation on the stored rate is that it must be `>= 1e18`:

```solidity
function _setRate(uint256 newRate) internal {
    if (newRate < 1e18) revert InvalidRate();
    rate = newRate;
    emit RateUpdated(newRate);
}
```

There is no `lastUpdated` timestamp, no maximum staleness window, and no on-chain mechanism to detect or reject a stale rate. The rate is returned verbatim to every caller:

```solidity
function getRate() external view returns (uint256) {
    return rate;
}
```

All L2 pool contracts call `IOracle(rsETHOracle).getRate()` inside `viewSwapRsETHAmountAndFee` to compute the rsETH output for a deposit:

```solidity
// RSETHPool / RSETHPoolV2 / RSETHPoolV3 (identical pattern)
uint256 rsETHToETHrate = getRate();
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

A lower-than-actual rate produces a larger `rsETHAmount`. Because rsETH accrues staking yield continuously on L1, the true rate rises monotonically over time. Every period between manual updates is therefore a window where the stored rate is below the true rate, and every depositor during that window receives excess rsETH.

For `RSETHPoolV2` and `RSETHPoolV3` variants, the excess rsETH is freshly minted (`wrsETH.mint(msg.sender, rsETHAmount)`), directly diluting all existing rsETH holders. For `RSETHPool`, the excess rsETH is transferred from the pool's own reserves, draining them.

---

### Impact Explanation

**High — Theft of unclaimed yield / dilution of existing rsETH holders.**

The excess rsETH minted or transferred represents staking yield that has accrued to existing rsETH holders but has not yet been reflected in the oracle. An attacker who deposits ETH during a stale-rate window receives rsETH tokens whose on-chain redemption value (set by `LRTOracle.rsETHPrice` on L1) is higher than the ETH they paid. The difference is extracted from the collective value backing all outstanding rsETH. For minting pools (`RSETHPoolV2`, `RSETHPoolV3`), this is an unbounded dilution of every rsETH holder proportional to the size of the deposit and the magnitude of the rate lag.

---

### Likelihood Explanation

**Medium.**

rsETH appreciates continuously and predictably. Manual rate updates require a privileged `MANAGER_ROLE` transaction, which introduces inherent latency (block confirmation, keeper uptime, gas conditions). No on-chain mechanism enforces a maximum update interval. An attacker needs only to observe the on-chain rate, compare it to the true rate (readable from `LRTOracle.rsETHPrice` on L1 or secondary markets), and call `deposit()` when a profitable gap exists. No special permissions, flash loans, or front-running are required.

---

### Recommendation

1. Replace `InterimRSETHOracle` with a pull-based oracle that reads `LRTOracle.rsETHPrice` directly (or via `RSETHPriceFeed`) so the rate is always current without manual intervention.
2. If a manual oracle must be retained, add a `lastUpdated` timestamp and revert in `getRate()` if `block.timestamp - lastUpdated > MAX_STALENESS` (e.g., 1 hour).
3. Add an upper-bound check in `_setRate` so the rate cannot be set below the previously recorded rate (rsETH should never depreciate under normal conditions), preventing accidental or malicious rate reductions.

---

### Proof of Concept

**Setup:**
- `InterimRSETHOracle.rate` = `1.005e18` (set 6 hours ago; rsETH was worth 1.005 ETH at that time).
- True current rsETH/ETH rate (from `LRTOracle.rsETHPrice` on L1) = `1.010e18` (staking rewards have accrued).
- `RSETHPoolV2` uses `InterimRSETHOracle` as `rsETHOracle`; `feeBps = 0` for simplicity.

**Attack:**
1. Attacker calls `RSETHPoolV2.deposit{value: 100 ether}("")`.
2. `viewSwapRsETHAmountAndFee(100 ether)` computes:
   - `rsETHAmount = 100e18 * 1e18 / 1.005e18 ≈ 99.502 rsETH`
3. At the true rate of `1.010e18`, those 99.502 rsETH are redeemable for `99.502 * 1.010 ≈ 100.497 ETH`.
4. Attacker deposited 100 ETH and holds rsETH worth ~100.497 ETH — a gain of ~0.497 ETH extracted from existing rsETH holders.
5. The attacker can repeat this every update cycle, scaling with deposit size and rate lag.

**Relevant code references:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/pools/oracle/InterimRSETHOracle.sol (L41-45)
```text
    function _setRate(uint256 newRate) internal {
        if (newRate < 1e18) revert InvalidRate();
        rate = newRate;
        emit RateUpdated(newRate);
    }
```

**File:** contracts/pools/oracle/InterimRSETHOracle.sol (L49-51)
```text
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/pools/RSETHPoolV2.sol (L207-218)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused limitDailyMint(msg.value) {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
```

**File:** contracts/pools/RSETHPoolV2.sol (L225-233)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPool.sol (L311-319)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```
