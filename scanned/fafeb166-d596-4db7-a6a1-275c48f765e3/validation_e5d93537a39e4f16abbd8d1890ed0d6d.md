### Title
Stale `rsETHPrice` Used in Deposit Calculations Without Prior Oracle Update - (File: `contracts/LRTDepositPool.sol`)

### Summary
`LRTDepositPool.depositETH` and `depositAsset` compute the amount of rsETH to mint using `lrtOracle.rsETHPrice()`, which is a **cached storage variable** that is only updated when `LRTOracle.updateRSETHPrice()` is explicitly called. Neither deposit function calls `updateRSETHPrice()` before reading this value. Because rewards continuously accrue in EigenLayer, the stored `rsETHPrice` is always slightly lower than the true current price between updates. Depositors who transact while the price is stale receive more rsETH than they are entitled to, diluting existing holders and constituting theft of unclaimed yield.

### Finding Description
`LRTDepositPool.getRsETHAmountToMint` computes the rsETH mint amount as:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

`lrtOracle.getAssetPrice(asset)` reads a live Chainlink feed and is always current. `lrtOracle.rsETHPrice()` reads the storage variable `rsETHPrice` in `LRTOracle`, which is only written inside `_updateRsETHPrice()`:

```solidity
rsETHPrice = newRsETHPrice;   // LRTOracle.sol line 313
```

`_updateRsETHPrice()` is triggered only by explicit calls to `updateRSETHPrice()` (public, permissionless) or `updateRSETHPriceAsManager()`. Neither `depositETH` nor `depositAsset` calls either of these before computing `rsethAmountToMint`.

As EigenLayer staking rewards accrue, the true rsETH/ETH rate rises continuously. Between oracle updates, `rsETHPrice` is lower than the actual current rate. A depositor who calls `depositETH` while the price is stale receives:

```
rsethAmountToMint = amount * assetPrice / staleLowerRsETHPrice
                  > amount * assetPrice / actualRsETHPrice
```

The excess rsETH minted is backed by no additional ETH, diluting every existing rsETH holder by extracting a portion of their accrued but not-yet-reflected yield.

The same stale read affects `LRTWithdrawalManager.getExpectedAssetAmount` (line 593), which is called by `initiateWithdrawal`. A stale (lower) `rsETHPrice` causes `expectedAssetAmount` to be set below the true entitlement, locking in a shortfall for the withdrawer that persists through `_calculatePayoutAmount`'s `min()` logic at `unlockQueue` time.

### Impact Explanation
**High — Theft of unclaimed yield.**

Every deposit made while `rsETHPrice` is stale mints excess rsETH. The excess is not backed by real ETH value; it is extracted from the unreflected yield belonging to existing rsETH holders. The magnitude scales with (a) the time elapsed since the last `updateRSETHPrice()` call and (b) the rate of EigenLayer reward accrual. Because `updateRSETHPrice()` is called off-chain by operators on a periodic schedule (not on every deposit), this condition is the normal operating state between updates.

### Likelihood Explanation
**Medium.** The stale-price window exists between every pair of consecutive `updateRSETHPrice()` calls. Any deposit during that window exploits the condition. A sophisticated actor can monitor the last-update timestamp and time deposits to maximise the stale gap. No special permissions are required; `depositETH` is open to any user.

### Recommendation
Call `updateRSETHPrice()` (or its internal equivalent `_updateRsETHPrice()`) at the start of `depositETH`, `depositAsset`, and `initiateWithdrawal` before reading `rsETHPrice`, mirroring the fix applied in the referenced Ion Protocol PR #30. This ensures all mint and withdrawal calculations use the current, freshly computed rate.

### Proof of Concept

1. At time T, `updateRSETHPrice()` is called. `rsETHPrice` is stored as `1.001e18` (1.001 ETH per rsETH).
2. EigenLayer rewards accrue. The true rate rises to `1.002e18` but `updateRSETHPrice()` has not been called again.
3. Alice calls `depositETH{value: 10 ether}()`.
4. `getRsETHAmountToMint` computes: `10e18 * 1e18 / 1.001e18 ≈ 9.990 rsETH` (using stale price).
5. The correct amount at the true rate would be: `10e18 * 1e18 / 1.002e18 ≈ 9.980 rsETH`.
6. Alice receives ~0.010 rsETH more than she is entitled to. This excess is extracted from the unreflected yield of all existing rsETH holders.
7. Alice immediately calls `updateRSETHPrice()`. The new price reflects the dilution; all existing holders now hold rsETH worth slightly less ETH than before Alice's deposit.

**Relevant code references:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/LRTDepositPool.sol (L515-521)
```text
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L311-313)
```text
        }

        rsETHPrice = newRsETHPrice;
```

**File:** contracts/LRTWithdrawalManager.sol (L589-594)
```text
        // setup oracle contract
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```
