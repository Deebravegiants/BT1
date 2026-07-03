### Title
`LRTOracle.rsETHPrice` Uninitialized at Deployment Causes Division-by-Zero in All Deposit Paths — (File: `contracts/LRTDepositPool.sol`)

---

### Summary

`LRTOracle.initialize()` does not set `rsETHPrice`, leaving it at the Solidity default of `0`. `LRTDepositPool.getRsETHAmountToMint` divides by `lrtOracle.rsETHPrice()` on every deposit. Until `updateRSETHPrice()` is explicitly called post-deployment, every call to `depositETH` and `depositAsset` reverts with a division-by-zero panic, making the protocol's primary entry point non-functional.

---

### Finding Description

`LRTOracle.initialize()` only sets `lrtConfig` and emits an event; it does not initialize `rsETHPrice`: [1](#0-0) 

`rsETHPrice` therefore starts at `0`. The only way to set it is through `_updateRsETHPrice()`, which is called by the public `updateRSETHPrice()` or the manager-gated `updateRSETHPriceAsManager()`. When `rsethSupply == 0` (the state at fresh deployment), `_updateRsETHPrice()` sets `rsETHPrice = 1 ether` and returns early: [2](#0-1) 

But this function is never called inside `initialize()`. Consequently, `rsETHPrice` remains `0` until an explicit post-deployment call is made.

`LRTDepositPool.getRsETHAmountToMint` divides by this uninitialized value: [3](#0-2) 

Both `depositETH` and `depositAsset` call `_beforeDeposit`, which calls `getRsETHAmountToMint`: [4](#0-3) [5](#0-4) 

A division by zero in Solidity 0.8.x triggers an arithmetic panic revert (`0x12`), so every deposit attempt fails until `updateRSETHPrice()` is called.

---

### Impact Explanation

**Low — Contract fails to deliver promised returns, but doesn't lose value.**

All user deposits via `depositETH` and `depositAsset` are completely blocked from the moment the contract is deployed until `updateRSETHPrice()` is called. No funds are at risk of theft or permanent loss, but the protocol's core deposit functionality is non-operational during this window.

---

### Likelihood Explanation

The window exists on every fresh deployment or proxy upgrade that resets `rsETHPrice`. Because `updateRSETHPrice()` is `public` (no role restriction), any caller — including the depositor themselves — can unblock the protocol by calling it first. However, the root cause (uninitialized state read in a critical computation path) is structurally identical to the reported Curve analog: a contract reads a state variable that was never set during initialization, causing the dependent function to always revert until an out-of-band call is made.

---

### Recommendation

Initialize `rsETHPrice` inside `LRTOracle.initialize()` by calling `_updateRsETHPrice()` at the end of initialization, or set `rsETHPrice = 1 ether` directly when `rsethSupply == 0`. This mirrors the fix suggested in the Curve report: ensure the state is valid before any dependent function can be called.

---

### Proof of Concept

1. Deploy `LRTOracle` proxy and call `initialize(lrtConfigAddr)`. `rsETHPrice` is `0`.
2. Deploy `LRTDepositPool` proxy and call `initialize(lrtConfigAddr)`.
3. Any user calls `depositETH{value: 1 ether}(0, "")`.
4. Execution reaches `getRsETHAmountToMint(ETH_TOKEN, 1 ether)`.
5. `lrtOracle.rsETHPrice()` returns `0`.
6. Solidity executes `(1e18 * assetPrice) / 0` → arithmetic panic revert `0x12`.
7. Deposit fails. All deposits fail identically until `updateRSETHPrice()` is called externally. [6](#0-5) [1](#0-0)

### Citations

**File:** contracts/LRTOracle.sol (L64-68)
```text
    function initialize(address lrtConfigAddr) external initializer {
        UtilLib.checkNonZeroAddress(lrtConfigAddr);
        lrtConfig = ILRTConfig(lrtConfigAddr);
        emit UpdatedLRTConfig(lrtConfigAddr);
    }
```

**File:** contracts/LRTOracle.sol (L218-222)
```text
        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }
```

**File:** contracts/LRTDepositPool.sol (L86-88)
```text
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

```

**File:** contracts/LRTDepositPool.sol (L111-111)
```text
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);
```

**File:** contracts/LRTDepositPool.sol (L506-521)
```text
    function getRsETHAmountToMint(
        address asset,
        uint256 amount
    )
        public
        view
        override
        returns (uint256 rsethAmountToMint)
    {
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```
