### Title
Division by Zero in `getRsETHAmountToMint` Due to Uninitialized `rsETHPrice` - (File: contracts/LRTDepositPool.sol)

### Summary
`LRTDepositPool.getRsETHAmountToMint` divides by `lrtOracle.rsETHPrice()` without a zero-check. The `rsETHPrice` storage variable in `LRTOracle` is initialized to `0` by default and is only set to a non-zero value after `updateRSETHPrice()` is explicitly called. If deposits are opened before that call is made, every deposit transaction reverts with a division-by-zero panic, temporarily freezing all deposit functionality.

### Finding Description
`LRTOracle.initialize()` does not set `rsETHPrice` to any non-zero value: [1](#0-0) 

`rsETHPrice` therefore starts at `0`. It is only updated inside `_updateRsETHPrice()`, which is reached via the public `updateRSETHPrice()` call: [2](#0-1) 

`LRTDepositPool.getRsETHAmountToMint` unconditionally divides by `lrtOracle.rsETHPrice()`: [3](#0-2) 

This function is called on every deposit path through `_beforeDeposit`: [4](#0-3) 

If `rsETHPrice == 0`, the division on line 520 panics and reverts the entire transaction.

### Impact Explanation
All user-facing deposit entry points (`depositETH`, `depositAsset`) are blocked until `updateRSETHPrice()` is called. No user funds can enter the protocol during this window. This constitutes a **temporary freezing of funds** (Medium severity per the allowed impact scope).

### Likelihood Explanation
The `LRTOracle` contract provides no automatic initialization of `rsETHPrice`. Deployment scripts or governance must explicitly call `updateRSETHPrice()` before enabling deposits. A missed or reordered initialization step — a realistic operational mistake — leaves the protocol in a state where every deposit reverts. The window can persist indefinitely until the call is made.

### Recommendation
Add a zero-check guard in `getRsETHAmountToMint` before dividing:

```solidity
uint256 currentRsETHPrice = lrtOracle.rsETHPrice();
if (currentRsETHPrice == 0) revert RsETHPriceNotInitialized();
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / currentRsETHPrice;
```

Alternatively, set `rsETHPrice` to `1 ether` inside `LRTOracle.initialize()` to guarantee a safe non-zero starting value, mirroring the guard already present in `_updateRsETHPrice` for the zero-supply case.

### Proof of Concept
1. Deploy `LRTOracle` and `LRTDepositPool` (do **not** call `updateRSETHPrice()`).
2. `LRTOracle.rsETHPrice()` returns `0`.
3. Any user calls `LRTDepositPool.depositETH{value: 1 ether}(0, "")`.
4. Execution reaches `getRsETHAmountToMint` → line 520: `(1e18 * assetPrice) / 0` → Solidity panic (division by zero), transaction reverts.
5. All deposits are blocked until a privileged or public caller invokes `updateRSETHPrice()`. [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/LRTOracle.sol (L64-68)
```text
    function initialize(address lrtConfigAddr) external initializer {
        UtilLib.checkNonZeroAddress(lrtConfigAddr);
        lrtConfig = ILRTConfig(lrtConfigAddr);
        emit UpdatedLRTConfig(lrtConfigAddr);
    }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L214-222)
```text
    function _updateRsETHPrice() internal {
        address rsETHTokenAddress = lrtConfig.rsETH();
        uint256 rsethSupply = IRSETH(rsETHTokenAddress).totalSupply();

        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }
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

**File:** contracts/LRTDepositPool.sol (L648-670)
```text
    function _beforeDeposit(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected
    )
        private
        view
        returns (uint256 rsethAmountToMint)
    {
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
    }
```
