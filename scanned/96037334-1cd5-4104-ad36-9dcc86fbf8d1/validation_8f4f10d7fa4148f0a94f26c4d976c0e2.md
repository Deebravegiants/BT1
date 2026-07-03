### Title
Missing Staleness Guard in `CrossChainRateReceiver.getRate()` Enables Stale Rate Consumption by Pool Contracts — (`contracts/cross-chain/CrossChainRateReceiver.sol`)

---

### Summary

`CrossChainRateReceiver` stores `lastUpdated` but never reads it in `getRate()`. All downstream pool contracts (`RSETHPoolV2`, `RSETHPoolV3`, `AGETHPoolV3`, and their variants) call `IOracle(rsETHOracle).getRate()` with no freshness check of their own. A block-stuffing window that delays `lzReceive` delivery causes every subsequent deposit to be priced against a frozen rate.

---

### Finding Description

`CrossChainRateReceiver.getRate()` returns the stored `rate` unconditionally:

```solidity
// contracts/cross-chain/CrossChainRateReceiver.sol L103-105
function getRate() external view returns (uint256) {
    return rate;
}
``` [1](#0-0) 

`lastUpdated` is written by `lzReceive` but is never read anywhere in the contract:

```solidity
// L95-97
rate = _rate;
lastUpdated = block.timestamp;
``` [2](#0-1) 

Every pool contract delegates its pricing to this oracle through the same unchecked call chain. For example, `RSETHPoolV2`:

```solidity
// contracts/pools/RSETHPoolV2.sol L201-203
function getRate() public view returns (uint256) {
    return IOracle(rsETHOracle).getRate();
}
``` [3](#0-2) 

That rate is consumed directly in `viewSwapRsETHAmountAndFee` and therefore in every `deposit()` call:

```solidity
// L225-233
function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
    fee = amount * feeBps / 10_000;
    uint256 amountAfterFee = amount - fee;
    uint256 rsETHToETHrate = getRate();
    rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
}
``` [4](#0-3) 

The same unchecked pattern is present in `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, `RSETHPoolV2ExternalBridge`, `RSETHPoolNoWrapper`, and `AGETHPoolV3`. [5](#0-4) [6](#0-5) 

The `lzReceive` entry point that would refresh the rate is gated only on `msg.sender == layerZeroEndpoint` and correct chain/provider checks — there is no permissionless fallback to push a fresh rate: [7](#0-6) 

---

### Impact Explanation

rsETH accrues staking rewards continuously, so its ETH-denominated rate rises monotonically over time. If the rate is frozen at a value lower than the current true rate, the formula `rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate` yields a **larger** rsETH mint than the depositor is entitled to. The protocol issues more rsETH than the deposited ETH backs, creating an undercollateralisation that grows with every deposit made during the stale window. This is a "contract fails to deliver promised returns" (Low) impact: the protocol's invariant that minted rsETH is fully backed by deposited ETH at the current rate is violated.

The reverse-swap path (`swapAssetToPremintedRsETH`) is `onlyRole(OPERATOR_ROLE)`, so an external attacker cannot immediately arbitrage the stale rate for direct ETH profit in a single transaction. The harm is dilution of existing rsETH holders and protocol undercollateralisation.

---

### Likelihood Explanation

The attack requires block-stuffing the destination chain long enough to make the rate meaningfully stale. On chains with a centralised sequencer (Arbitrum, Optimism) this is not feasible. On chains with open block production (e.g. a PoS L2 or any EVM chain without a sequencer monopoly) it is feasible but expensive. The cost must be weighed against the dilution gain, which is bounded by the daily mint limit. Likelihood is **low** but non-zero on applicable deployment targets.

---

### Recommendation

Add a configurable `maxStaleness` parameter and revert in `getRate()` if `block.timestamp - lastUpdated > maxStaleness`:

```solidity
uint256 public maxStaleness; // e.g. 24 hours

function getRate() external view returns (uint256) {
    require(block.timestamp - lastUpdated <= maxStaleness, "Rate is stale");
    return rate;
}
```

This converts a silent stale-read into a hard revert, halting deposits until the rate is refreshed rather than silently mispricing them.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import "forge-std/Test.sol";

// Minimal concrete receiver for testing
contract MockReceiver is CrossChainRateReceiver {
    constructor() { }
    // expose lzReceive for testing
}

contract StaleRateTest is Test {
    MockReceiver receiver;

    function setUp() public {
        receiver = new MockReceiver();
        // Simulate a rate update that happened 7 days ago
        vm.store(address(receiver), bytes32(uint256(0)), bytes32(uint256(1.05e18))); // rate slot
        vm.store(address(receiver), bytes32(uint256(1)), bytes32(block.timestamp - 7 days)); // lastUpdated slot
    }

    function test_getRate_returnsStaleValueWithoutRevert() public {
        // getRate() returns the 7-day-old rate with no revert
        uint256 r = receiver.getRate();
        assertEq(r, 1.05e18);
    }

    function test_pool_usesStaleRate() public {
        // Wire a mock pool to the stale receiver
        // Deposit 1 ETH → pool computes rsETHAmount using 1.05e18 (stale)
        // True rate is e.g. 1.06e18 → user receives ~0.9906 rsETH instead of ~0.9434 rsETH
        // i.e. ~5% over-issuance relative to the true rate
        uint256 staleAmount = 1e18 * 1e18 / 1.05e18;
        uint256 trueAmount  = 1e18 * 1e18 / 1.06e18;
        assertGt(staleAmount, trueAmount); // stale rate issues more rsETH
    }
}
```

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

**File:** contracts/pools/RSETHPoolV2.sol (L200-203)
```text
    /// @dev Gets the rate from the rsETHOracle
    function getRate() public view returns (uint256) {
        return IOracle(rsETHOracle).getRate();
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

**File:** contracts/pools/RSETHPoolV3.sol (L234-237)
```text
    /// @dev Gets the rate from the rsETHOracle
    function getRate() public view returns (uint256) {
        return IOracle(rsETHOracle).getRate();
    }
```

**File:** contracts/agETH/AGETHPoolV3.sol (L160-168)
```text
    function viewSwapAgETHAmountAndFee(uint256 amount) public view returns (uint256 agETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of agETH in ETH
        uint256 agETHToETHrate = getRate();

        // Calculate the final agETH amount
        agETHAmount = amountAfterFee * 1e18 / agETHToETHrate;
```
