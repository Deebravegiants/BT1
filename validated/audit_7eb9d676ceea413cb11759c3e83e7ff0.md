### Title
`LRTDepositPool.depositETH`/`depositAsset` Mint rsETH Using Stale `rsETHPrice` Without Triggering a Price Update, Allowing Deposits at Incorrect Rates That Dilute Existing Holders - (File: contracts/LRTDepositPool.sol)

---

### Summary

`LRTDepositPool.depositETH()` and `depositAsset()` calculate the rsETH amount to mint using the stored `rsETHPrice` from `LRTOracle`, which is only updated when `updateRSETHPrice()` is explicitly called. If the protocol's TVL has grown (rewards accrued) but `updateRSETHPrice()` has not yet been called, the stored price is stale-low. New depositors receive more rsETH than they are entitled to, diluting existing holders' yield — directly analogous to M-17, where a new loan is issued to a user who should be liquidated because the liquidation trigger has not yet been pulled.

---

### Finding Description

`LRTDepositPool.depositETH()` and `depositAsset()` both call `_beforeDeposit()`, which calls `getRsETHAmountToMint()`:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

`lrtOracle.rsETHPrice()` returns the **stored** value of `rsETHPrice` in `LRTOracle`, not a freshly computed value. This stored value is only updated when `updateRSETHPrice()` (or `updateRSETHPriceAsManager()`) is called. Neither `depositETH()` nor `depositAsset()` trigger a price update before minting.

`LRTOracle._updateRsETHPrice()` contains a threshold guard: if the newly computed price exceeds `highestRsethPrice` by more than `pricePercentageLimit`, non-manager callers receive `PriceAboveDailyThreshold` and the update reverts. This creates a concrete window during which:

1. The protocol's actual TVL (and thus the true rsETH price) has risen above the stored value.
2. Public calls to `updateRSETHPrice()` revert.
3. Only the manager can update via `updateRSETHPriceAsManager()`, but this is not guaranteed to happen immediately.

During this window, `rsETHPrice` is stale-low. The minting formula divides by a denominator that is smaller than the true price, so depositors receive **more rsETH than they are entitled to**. This excess rsETH represents a transfer of value from existing holders to the new depositor.

The root cause mirrors M-17 exactly: the deposit path checks an **external state** (`rsETHPrice`) that is only updated by an **external trigger** (`updateRSETHPrice()`). If that trigger has not fired, the check passes with a stale value, and a new position is created at incorrect terms.

---

### Impact Explanation

**Impact: High — Theft of unclaimed yield.**

When `rsETHPrice` is stale-low, each new deposit mints excess rsETH. Because rsETH is a share token backed by a fixed pool of assets, excess shares dilute the value of every existing holder's position. The attacker can then wait for `updateRSETHPrice()` to be called (price rises to reflect true TVL), and redeem their inflated rsETH balance for more underlying assets than they deposited. The profit comes directly from existing rsETH holders' accrued yield.

Concrete example:
- True rsETH price: 1.05 ETH (rewards accrued, not yet recorded).
- Stored `rsETHPrice`: 1.00 ETH (stale).
- Attacker deposits 1 ETH → receives `1e18 * 1e18 / 1e18 = 1 rsETH` (should receive ≈ 0.952 rsETH).
- `updateRSETHPrice()` is called; stored price updates to 1.05 ETH.
- Attacker redeems 1 rsETH → receives 1.05 ETH.
- Net profit: 0.05 ETH extracted from existing holders' yield.

---

### Likelihood Explanation

**Likelihood: Medium.**

The stale-price window opens whenever the true rsETH price has risen faster than `pricePercentageLimit` allows non-managers to record. This is a normal operational condition (rewards accrue continuously), not an exotic edge case. The window closes only when the manager calls `updateRSETHPriceAsManager()`. Any delay — due to operational latency, key management, or deliberate front-running — extends the exploitable window. A sophisticated actor monitoring on-chain TVL can detect the discrepancy and act before the price is updated.

---

### Recommendation

Before minting rsETH, `LRTDepositPool` should attempt to update the oracle price (or verify it is fresh). One approach:

1. Call `lrtOracle.updateRSETHPrice()` at the start of `depositETH()` / `depositAsset()`, and proceed only if it succeeds (or if the caller is a manager who can override the threshold).
2. Alternatively, add a staleness timestamp to `LRTOracle` and revert deposits if `rsETHPrice` has not been updated within an acceptable window (e.g., 24 hours).

---

### Proof of Concept

**Entry path (unprivileged depositor):**

1. Rewards accrue in EigenLayer strategies; `getTotalAssetDeposits()` returns a higher ETH value than before.
2. The true rsETH price (computed by `_getTotalEthInProtocol() / rsethSupply`) now exceeds `highestRsethPrice * (1 + pricePercentageLimit)`.
3. Any call to `updateRSETHPrice()` by a non-manager reverts with `PriceAboveDailyThreshold`.
4. Attacker calls `LRTDepositPool.depositETH{value: X}(minRSETH, "")`.
5. `_beforeDeposit()` → `getRsETHAmountToMint()` → `(X * 1e18) / rsETHPrice` uses the stale (lower) stored price → mints excess rsETH to attacker.
6. Manager eventually calls `updateRSETHPriceAsManager()`, stored price rises.
7. Attacker calls `LRTWithdrawalManager.initiateWithdrawal()` and later `completeWithdrawal()`, redeeming excess rsETH at the now-correct higher price.
8. Attacker extracts the yield delta that belonged to pre-existing rsETH holders.

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

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

**File:** contracts/LRTOracle.sol (L87-96)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }

    /// @dev update rsETH price as an manager account
    /// @dev main benefit is to be able to update the price in case of the price going above the threshold
    /// @dev only LRT manager is allowed to call this function
    function updateRSETHPriceAsManager() external onlyLRTManager {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L252-267)
```text
        if (newRsETHPrice > highestRsethPrice) {
            // check if the price is above the threshold
            uint256 priceDifference = newRsETHPrice - highestRsethPrice;
            // pricePercentageLimit is in 1e18 precision (100% = 1e18, 1% = 1e16)
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);

            // check if the price difference is above the threshold
            if (isPriceIncreaseOffLimit) {
                // if sender has a manager role, this doesn't revert.
                // if not, it reverts as price went above the threshold
                if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
                    revert PriceAboveDailyThreshold();
                }
            }
        }
```

**File:** contracts/LRTOracle.sol (L299-313)
```text
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
            }
        } else {
            _checkAndUpdateDailyFeeMintLimit(0);
        }

        rsETHPrice = newRsETHPrice;
```
