Looking at the code carefully across all relevant contracts:

### Title
Missing Zero-Rate Guard in `setAgETHOracle` Causes Division-by-Zero on All Deposits — (`contracts/agETH/AGETHPoolV3.sol`)

---

### Summary

`AGETHPoolV3.setAgETHOracle` accepts any non-zero address as the new oracle without verifying that `getRate()` returns a non-zero value. A freshly deployed `AGETHRateReceiver` has `rate = 0` until its first LayerZero message arrives. If the admin points the pool at such a receiver before `lzReceive` is called, every ETH and token deposit reverts with a division-by-zero panic, freezing the deposit path until an admin intervenes.

---

### Finding Description

**Root cause — `CrossChainRateReceiver.rate` defaults to zero:**

`CrossChainRateReceiver` declares `rate` as a plain `uint256` storage variable with no initializer. [1](#0-0) 

`AGETHRateReceiver`'s constructor sets `rateInfo`, `srcChainId`, `rateProvider`, and `layerZeroEndpoint`, but never sets `rate`, so it remains `0` until the first `lzReceive` call. [2](#0-1) 

**Root cause — `setAgETHOracle` has no rate validation:**

```solidity
function setAgETHOracle(address _agETHOracle) external onlyRole(DEFAULT_ADMIN_ROLE) {
    UtilLib.checkNonZeroAddress(_agETHOracle);   // only checks address != 0
    agETHOracle = _agETHOracle;
    emit OracleSet(_agETHOracle);
}
``` [3](#0-2) 

This is inconsistent with `addSupportedToken`, which explicitly rejects an oracle whose `getRate()` returns zero: [4](#0-3) 

**Root cause — `viewSwapAgETHAmountAndFee` divides by the rate without a zero guard:**

```solidity
uint256 agETHToETHrate = getRate();
agETHAmount = amountAfterFee * 1e18 / agETHToETHrate;   // panics if rate == 0
``` [5](#0-4) 

Both the ETH deposit path and the token deposit path call this function: [6](#0-5) [7](#0-6) 

**Note on the RSETHPoolV3 comparison:** The question states RSETHPoolV3 "reverts on zero rate" in its deposit path. This is only true for `viewSwapAssetToPremintedRsETH` (the reverse-swap path). [8](#0-7) 
`RSETHPoolV3.viewSwapRsETHAmountAndFee` (the forward deposit path) also lacks a zero-rate guard. [9](#0-8) 
This does not invalidate the AGETHPoolV3 finding; it means the same class of bug exists in RSETHPoolV3's deposit path as well.

---

### Impact Explanation

**Medium — Temporary freezing of funds.**

Every call to `deposit(string)` or `deposit(address,uint256,string)` reverts with a Solidity division-by-zero panic for as long as `agETHOracle.getRate()` returns `0`. No ETH or tokens are lost (the ETH reverts back to the caller), but the deposit path is completely non-functional during this window. The freeze ends only when the admin either (a) calls `setAgETHOracle` again with a live oracle, or (b) waits for the first LayerZero message to populate `rate`.

---

### Likelihood Explanation

Oracle upgrades and migrations are routine operational events. An admin deploying a new `AGETHRateReceiver` and immediately calling `setAgETHOracle` before the first cross-chain rate message arrives is a realistic and foreseeable sequence. The window can last minutes to hours depending on LayerZero message latency and the rate-update schedule. No attacker action is required to trigger the freeze; the admin's own legitimate upgrade action is sufficient.

---

### Recommendation

Add a zero-rate check in `setAgETHOracle`, mirroring the guard already present in `addSupportedToken`:

```solidity
function setAgETHOracle(address _agETHOracle) external onlyRole(DEFAULT_ADMIN_ROLE) {
    UtilLib.checkNonZeroAddress(_agETHOracle);
    if (IOracle(_agETHOracle).getRate() == 0) revert UnsupportedOracle();
    agETHOracle = _agETHOracle;
    emit OracleSet(_agETHOracle);
}
```

Apply the same fix to `RSETHPoolV3.setRSETHOracle` and any equivalent setter in other pool variants, and add a zero-rate guard inside `viewSwapAgETHAmountAndFee` / `viewSwapRsETHAmountAndFee` as a defence-in-depth measure.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Minimal unit test (Foundry)
contract ZeroRatePoC is Test {
    AGETHPoolV3 pool;
    AGETHRateReceiver freshReceiver;

    function setUp() public {
        // Deploy pool (simplified — use a mock agETH that allows mint)
        pool = new AGETHPoolV3();
        pool.initialize(address(this), address(this), address(mockAgETH), 0, address(someInitialOracle));

        // Deploy a fresh receiver — rate is 0, no lzReceive yet
        freshReceiver = new AGETHRateReceiver(1, address(0x1), address(0x2));
        assertEq(freshReceiver.getRate(), 0);

        // Admin points pool at the uninitialized receiver
        pool.setAgETHOracle(address(freshReceiver));
    }

    function test_depositRevertsOnZeroRate() public {
        vm.expectRevert(); // division-by-zero panic
        pool.deposit{value: 1 ether}("ref");
    }
}
```

The test deploys a fresh `AGETHRateReceiver`, sets it as the pool oracle via `setAgETHOracle`, and asserts that `deposit` reverts — confirming the freeze without any attacker involvement beyond the admin's own upgrade action.

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L13-13)
```text
    uint256 public rate;
```

**File:** contracts/agETH/AGETHRateReceiver.sol (L10-15)
```text
    constructor(uint16 _srcChainId, address _rateProvider, address _layerZeroEndpoint) {
        rateInfo = RateInfo({ tokenSymbol: "agETH", baseTokenSymbol: "ETH" });
        srcChainId = _srcChainId;
        rateProvider = _rateProvider;
        layerZeroEndpoint = _layerZeroEndpoint;
    }
```

**File:** contracts/agETH/AGETHPoolV3.sol (L121-121)
```text
        (uint256 agETHAmount, uint256 fee) = viewSwapAgETHAmountAndFee(amount);
```

**File:** contracts/agETH/AGETHPoolV3.sol (L147-147)
```text
        (uint256 agETHAmount, uint256 fee) = viewSwapAgETHAmountAndFee(amount, token);
```

**File:** contracts/agETH/AGETHPoolV3.sol (L165-168)
```text
        uint256 agETHToETHrate = getRate();

        // Calculate the final agETH amount
        agETHAmount = amountAfterFee * 1e18 / agETHToETHrate;
```

**File:** contracts/agETH/AGETHPoolV3.sol (L262-268)
```text
    function setAgETHOracle(address _agETHOracle) external onlyRole(DEFAULT_ADMIN_ROLE) {
        UtilLib.checkNonZeroAddress(_agETHOracle);

        agETHOracle = _agETHOracle;

        emit OracleSet(_agETHOracle);
    }
```

**File:** contracts/agETH/AGETHPoolV3.sol (L279-281)
```text
        if (IOracle(oracle).getRate() == 0) {
            revert UnsupportedOracle();
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

**File:** contracts/pools/RSETHPoolV3.sol (L393-393)
```text
        if (rsETHToETHrate == 0) revert UnsupportedOracle();
```
