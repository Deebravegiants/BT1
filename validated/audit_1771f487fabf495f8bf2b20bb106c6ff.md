### Title
Stale Cross-Chain Rate Used for rsETH Minting Without Staleness Check — (`contracts/cross-chain/CrossChainRateReceiver.sol`)

### Summary

`CrossChainRateReceiver.getRate()` returns a cached `rate` with no staleness validation. All L2 pool contracts (`RSETHPool`, `RSETHPoolV2`, `RSETHPoolV3`, `RSETHPoolV3WithNativeChainBridge`, etc.) call this function to determine how many rsETH tokens to mint per ETH deposited. When the L1 rsETH price has risen but the L2 oracle has not been updated, depositors receive more rsETH than they are entitled to, diluting existing holders' accumulated yield.

### Finding Description

`CrossChainRateReceiver` stores two fields: `rate` (the last received rsETH/ETH exchange rate) and `lastUpdated` (the timestamp of the last update). The `getRate()` function unconditionally returns `rate` without comparing `lastUpdated` to `block.timestamp`:

```solidity
// CrossChainRateReceiver.sol line 103-105
function getRate() external view returns (uint256) {
    return rate;
}
```

The rate is only refreshed when a LayerZero message is received via `lzReceive()`. There is no keeper obligation, no on-chain heartbeat enforcement, and no revert path if the rate is arbitrarily old.

Every L2 pool's `deposit()` path calls `IOracle(rsETHOracle).getRate()` through `viewSwapRsETHAmountAndFee()`:

```solidity
// RSETHPoolV3.sol line 299-308
function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
    fee = amount * feeBps / 10_000;
    uint256 amountAfterFee = amount - fee;
    uint256 rsETHToETHrate = getRate();          // ← stale rate, no check
    rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
}
```

Because rsETH continuously accrues value (staking + restaking rewards), the true L1 rate grows monotonically. A stale (lower) rate causes the division to yield a larger `rsETHAmount`, minting excess rsETH to the depositor.

The same pattern is present in `RSETHPool.viewSwapRsETHAmountAndFee()`, `RSETHPoolV2.viewSwapRsETHAmountAndFee()`, `RSETHPoolV3WithNativeChainBridge.viewSwapRsETHAmountAndFee()`, and their token-denominated overloads.

### Impact Explanation

**High — Theft of unclaimed yield.**

rsETH is a yield-bearing token: its ETH redemption value increases over time as staking and restaking rewards accumulate on L1. When the L2 oracle rate lags behind the true L1 rate, a depositor pays 1 ETH but receives rsETH priced at the old (lower) rate, i.e., more rsETH than 1 ETH currently buys on L1. When those tokens are later redeemed or traded at the current (higher) rate, the depositor extracts value that belongs to existing rsETH holders. The magnitude scales with the rate gap and the deposit size; a 0.5% rate lag on a 1,000 ETH deposit yields ~5 ETH of stolen yield.

### Likelihood Explanation

**Medium.** The rate update is not automatic. It requires an off-chain actor to call `CrossChainRateProvider.updateRate()` and pay LayerZero fees. During periods of high gas prices, network congestion, or keeper downtime, the rate can remain stale for hours or days. rsETH accrues value continuously (~4–6% APY), so even a 24-hour staleness window creates a measurable exploitable gap. Any unprivileged depositor can observe `lastUpdated` on-chain and time their deposit to coincide with maximum staleness.

### Recommendation

1. Add a `maxStaleness` parameter to `CrossChainRateReceiver` and revert in `getRate()` if `block.timestamp - lastUpdated > maxStaleness`.
2. Alternatively, have the L2 pool contracts check `lastUpdated` before accepting deposits and revert or pause if the rate is stale beyond a configured threshold.
3. Implement an automated keeper or Chainlink Automation job to push rate updates on a regular heartbeat.

### Proof of Concept

1. At `T=0`, the L2 oracle rate is `1.050e18` (rsETH/ETH). The true L1 rate is also `1.050e18`.
2. No `updateRate()` call is made for 48 hours. The true L1 rate grows to `1.056e18` (~0.57% increase).
3. Attacker calls `RSETHPoolV3.deposit{value: 1000 ether}("")` on L2.
4. `viewSwapRsETHAmountAndFee(1000e18)` computes `rsETHAmount = 1000e18 * 1e18 / 1.050e18 ≈ 952.38 rsETH`.
5. At the current L1 rate, 952.38 rsETH is worth `952.38 * 1.056e18 / 1e18 ≈ 1005.71 ETH`.
6. Attacker deposited 1000 ETH and holds rsETH worth 1005.71 ETH — a ~5.71 ETH gain extracted from existing holders' accumulated yield.
7. `CrossChainRateReceiver.lastUpdated` is publicly readable, making the staleness window trivially observable before executing the deposit.

---

**Affected files and lines:**

- `contracts/cross-chain/CrossChainRateReceiver.sol` — `getRate()` at line 103–105: no staleness check on `lastUpdated` [1](#0-0) 

- `contracts/pools/RSETHPoolV3.sol` — `viewSwapRsETHAmountAndFee()` at line 299–308: uses stale rate for mint calculation [2](#0-1) 

- `contracts/pools/RSETHPool.sol` — `viewSwapRsETHAmountAndFee()` at line 311–320: same pattern [3](#0-2) 

- `contracts/cross-chain/CrossChainRateReceiver.sol` — `lzReceive()` at line 82–100: only update path, no heartbeat enforcement [4](#0-3)

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L82-100)
```text
    function lzReceive(uint16 _srcChainId, bytes memory _srcAddress, uint64, bytes calldata _payload) external {
        require(msg.sender == layerZeroEndpoint, "Sender should be lz endpoint");

        address srcAddress;
        assembly {
            srcAddress := mload(add(_srcAddress, 20))
        }

        require(_srcChainId == srcChainId, "Src chainId must be correct");
        require(srcAddress == rateProvider, "Src address must be provider");

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

**File:** contracts/pools/RSETHPool.sol (L311-320)
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
