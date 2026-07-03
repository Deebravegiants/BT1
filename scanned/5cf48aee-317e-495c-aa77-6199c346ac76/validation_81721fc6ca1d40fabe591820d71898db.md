### Title
Division by Zero in `getRsETHAmountToMint()` When `rsETHPrice` Is Uninitialized Blocks All Deposits - (File: contracts/LRTDepositPool.sol)

### Summary
`LRTDepositPool.getRsETHAmountToMint()` divides by `lrtOracle.rsETHPrice()` without a zero-check. The `rsETHPrice` storage variable in `LRTOracle` defaults to `0` and is only set by a call to `updateRSETHPrice()`. In the window between deployment and the first successful `updateRSETHPrice()` call, every user deposit reverts with a division-by-zero panic, temporarily freezing all deposit functionality.

### Finding Description
`LRTDepositPool.getRsETHAmountToMint()` computes the rsETH mint amount as:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

`lrtOracle.rsETHPrice()` reads the public storage variable `rsETHPrice` from `LRTOracle`. This variable is declared as:

```solidity
uint256 public override rsETHPrice;
```

with no initializer value, so it starts at `0`. It is only written inside `_updateRsETHPrice()`, which is called by `updateRSETHPrice()` (public, permissionless) or `updateRSETHPriceAsManager()` (manager-only). There is no check in `getRsETHAmountToMint()` or its callers that `rsETHPrice != 0` before performing the division.

`_updateRsETHPrice()` does handle the `rsethSupply == 0` case by setting `rsETHPrice = 1 ether`, but this only executes after `updateRSETHPrice()` is explicitly called. Until that happens, `rsETHPrice` remains `0`.

The call chain that hits the division is:

1. User calls `depositETH()` or `depositAsset()` on `LRTDepositPool`
2. `_beforeDeposit()` calls `getRsETHAmountToMint()`
3. `getRsETHAmountToMint()` executes `/ lrtOracle.rsETHPrice()` → division by zero → revert

### Impact Explanation
All user deposits (`depositETH`, `depositAsset`) are blocked for the entire period during which `rsETHPrice == 0`. No funds are lost, but the core deposit function of the protocol is completely non-functional. This constitutes **temporary freezing of funds** (medium impact).

### Likelihood Explanation
The window exists at every fresh deployment of `LRTOracle`. Because the contract is upgradeable (`Initializable`), a re-initialization scenario or a fresh deployment without an immediate `updateRSETHPrice()` call reproduces the condition. Any user who attempts a deposit in this window triggers the revert. Likelihood is **medium** — the window is short in practice but is structurally guaranteed to exist and requires no attacker action to exploit.

### Recommendation
Add a zero-check guard in `getRsETHAmountToMint()`:

```solidity
uint256 currentRsETHPrice = lrtOracle.rsETHPrice();
if (currentRsETHPrice == 0) revert RsETHPriceNotInitialized();
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / currentRsETHPrice;
```

Alternatively, enforce that `rsETHPrice` is set to a non-zero sentinel (e.g., `1 ether`) during `LRTOracle.initialize()`, mirroring the logic already present in `_updateRsETHPrice()` for the zero-supply case.

### Proof of Concept
1. Deploy `LRTOracle` (fresh). `rsETHPrice` storage slot = `0`.
2. Deploy `LRTDepositPool` pointing to the above oracle.
3. Do **not** call `updateRSETHPrice()`.
4. Call `depositETH{value: 1 ether}(0, "")` as any EOA.
5. Execution reaches `getRsETHAmountToMint()` → `(1e18 * assetPrice) / 0` → EVM division-by-zero panic → transaction reverts.
6. All deposits are blocked until a separate `updateRSETHPrice()` transaction is mined. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/LRTDepositPool.sol (L519-520)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/LRTDepositPool.sol (L648-669)
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
```

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
```

**File:** contracts/LRTOracle.sol (L218-222)
```text
        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }
```
