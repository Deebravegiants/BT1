### Title
`getAaveAvailableCapacity()` Omits Reserve Status Check, Returning Inflated Capacity When WETH Reserve Is Inactive — (`contracts/LRTWithdrawalManager.sol`)

---

### Summary

`getAaveAvailableCapacity()` only queries `getReserveCaps()` to compute remaining deposit room, but never calls `getReserveConfigurationData()` to verify `isActive` or `isFrozen`. When the Aave WETH reserve is inactive, the function returns a non-zero (or `type(uint256).max`) value while every actual deposit attempt silently fails via the `try/catch` in `unlockQueue`, leaving ETH idle and earning no yield.

---

### Finding Description

`getAaveAvailableCapacity()` is implemented as follows: [1](#0-0) 

It calls only `aaveDataProvider.getReserveCaps(WETH_ADDRESS)` to determine available capacity. The `IPoolDataProvider` interface also exposes `getReserveConfigurationData()`, which returns `isActive` and `isFrozen`: [2](#0-1) 

Neither flag is ever consulted. When the WETH reserve is inactive (`isActive = false`) or frozen (`isFrozen = true`), `getReserveCaps` still returns the configured cap, so `getAaveAvailableCapacity()` returns a positive value.

The actual deposit path in `unlockQueue` wraps the call in a `try/catch`: [3](#0-2) 

When the reserve is inactive, `depositETH` reverts, the catch block emits `AaveDepositFailed`, and ETH remains in the contract. The view function continues to report available capacity, creating a persistent mismatch: operators querying `getAaveAvailableCapacity()` see a non-zero value and have no on-chain signal that deposits are structurally failing.

The same gap affects `depositIdleETHToAave`, which calls `_depositToAave` directly: [4](#0-3) 

This function also has no pre-check for reserve status, so a manual operator attempt to deposit idle ETH will also revert without a clear diagnostic.

---

### Impact Explanation

ETH unlocked via `unlockQueue` is intended to be deposited into Aave to earn yield until users claim. When the reserve is inactive, every auto-deposit silently fails, ETH accumulates idle in the contract, and no yield accrues. The contract fails to deliver its promised Aave yield returns. No principal is lost — user withdrawals remain serviceable — so this is a **Low** severity finding: contract fails to deliver promised returns, but doesn't lose value.

---

### Likelihood Explanation

Aave V3 reserves can be deactivated by Aave governance or the Aave emergency admin (a multisig). This is an external trigger, but it is a documented, exercised mechanism (used during past incidents). Once triggered, the condition persists indefinitely until governance re-activates the reserve. The LRT contract has no automated detection or alerting beyond the `AaveDepositFailed` event, which operators must actively monitor off-chain. The likelihood of a prolonged silent yield loss is moderate given the reliance on off-chain monitoring.

---

### Recommendation

Add a reserve-status pre-check inside `getAaveAvailableCapacity()` (and optionally `depositIdleETHToAave`) using `getReserveConfigurationData()`:

```solidity
(,,,,,,,, bool isActive, bool isFrozen) =
    aaveDataProvider.getReserveConfigurationData(WETH_ADDRESS);
if (!isActive || isFrozen) return 0;
```

This makes the view function accurately reflect depositability and allows operators and off-chain tooling to detect the inactive-reserve condition without parsing event logs.

---

### Proof of Concept

```solidity
// Fork test (Foundry, mainnet fork)
// 1. Deploy/configure LRTWithdrawalManager with Aave integration enabled.
// 2. Impersonate Aave emergency admin; call Pool.setReserveActive(WETH, false).
// 3. Call unlockQueue for ETH asset.
//    -> depositToAaveExternal reverts; AaveDepositFailed is emitted.
//    -> ETH balance of LRTWithdrawalManager increases.
// 4. Call getAaveAvailableCapacity().
//    -> Returns > 0 (or type(uint256).max if supplyCap == 0).
// Assert: AaveDepositFailed was emitted AND getAaveAvailableCapacity() > 0.
// This proves the invariant is broken: capacity > 0 while deposits always revert.
```

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L309-317)
```text
        // If Aave integration is enabled and asset is ETH, deposit to Aave
        if (isAaveIntegrationEnabled && asset == LRTConstants.ETH_TOKEN && assetAmountUnlocked > 0) {
            try this.depositToAaveExternal(assetAmountUnlocked) { }
            catch (bytes memory reason) {
                emit AaveDepositFailed(assetAmountUnlocked, reason);
                // Silently fail if Aave deposit fails (e.g., pool at max capacity)
                // Funds remain in contract for withdrawals
            }
        }
```

**File:** contracts/LRTWithdrawalManager.sol (L521-534)
```text
    function depositIdleETHToAave(uint256 amount) external nonReentrant whenNotPaused onlyLRTOperator {
        if (!isAaveIntegrationEnabled) revert AaveIntegrationNotEnabled();

        uint256 idleBalance = address(this).balance;
        if (idleBalance == 0) revert AmountMustBeGreaterThanZero();

        uint256 depositAmount = amount;
        if (amount == type(uint256).max || amount > idleBalance) {
            depositAmount = idleBalance;
        }

        if (depositAmount > 0) {
            _depositToAave(depositAmount);
        }
```

**File:** contracts/LRTWithdrawalManager.sol (L659-679)
```text
    function getAaveAvailableCapacity() external view returns (uint256 availableCapacity) {
        if (address(aaveAWETH) == address(0) || address(aaveDataProvider) == address(0)) {
            revert InvalidAaveConfiguration();
        }

        // Get supply cap from Aave Data Provider
        (, uint256 supplyCap) = aaveDataProvider.getReserveCaps(WETH_ADDRESS);

        // If supply cap is 0, it means unlimited capacity
        if (supplyCap == 0) return type(uint256).max;

        // Get current total supply of aWETH
        uint256 totalSupply = aaveAWETH.totalSupply();

        // Convert supply cap to wei and calculate available capacity
        uint256 supplyCapWei = supplyCap * 1e18;
        if (supplyCapWei > totalSupply) {
            availableCapacity = supplyCapWei - totalSupply;
        }
        // else returns 0 (pool is at or over capacity)
    }
```

**File:** contracts/interfaces/aave/IPoolDataProvider.sol (L24-38)
```text
    function getReserveConfigurationData(address asset)
        external
        view
        returns (
            uint256 decimals,
            uint256 ltv,
            uint256 liquidationThreshold,
            uint256 liquidationBonus,
            uint256 reserveFactor,
            bool usageAsCollateralEnabled,
            bool borrowingEnabled,
            bool stableBorrowRateEnabled,
            bool isActive,
            bool isFrozen
        );
```
