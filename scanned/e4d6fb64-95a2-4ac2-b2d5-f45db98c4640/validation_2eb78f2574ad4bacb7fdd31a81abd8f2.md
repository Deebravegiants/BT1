### Title
First Depositor ETH Donation Inflates rsETH Price, Enabling Fund Theft from Depositors with Zero Slippage Guard - (File: contracts/LRTDepositPool.sol)

### Summary
The `LRTDepositPool` contract accepts unrestricted ETH donations via its `receive()` function. Because `getETHDistributionData()` reads `address(this).balance` directly, any donated ETH inflates `totalETHInProtocol`, which `LRTOracle._updateRsETHPrice()` uses to compute `rsETHPrice`. When `pricePercentageLimit` is zero (its default value, never set in `initialize()`), an attacker can be the first depositor, donate ETH to inflate the price without bound, and cause a subsequent depositor who passes `minRSETHAmountExpected = 0` to receive zero rsETH while their ETH remains in the protocol — a direct theft.

### Finding Description

**Step 1 — Donation vector is open to anyone.**

`LRTDepositPool` exposes four unrestricted payable entry points:

```solidity
receive() external payable { }
function receiveFromRewardReceiver() external payable { }
function receiveFromLRTConverter() external payable { }
function receiveFromNodeDelegator() external payable { }
```

None carry access control. Any caller can increase `address(this).balance`. [1](#0-0) 

**Step 2 — Donated ETH is counted as protocol TVL.**

`getETHDistributionData()` returns `address(this).balance` as `ethLyingInDepositPool`:

```solidity
ethLyingInDepositPool = address(this).balance;
``` [2](#0-1) 

`getTotalAssetDeposits` aggregates this into the total, which `LRTOracle._getTotalEthInProtocol()` then reads. [3](#0-2) 

**Step 3 — Price update has no floor guard when `pricePercentageLimit == 0`.**

`_updateRsETHPrice()` computes:

```solidity
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

The only upside guard is:

```solidity
bool isPriceIncreaseOffLimit =
    pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
```

`pricePercentageLimit` is **never initialised** in `initialize()`, so it defaults to `0`. The condition `pricePercentageLimit > 0` is always `false`, making `isPriceIncreaseOffLimit = false` and the guard a no-op. The price can be inflated to any value. [4](#0-3) [5](#0-4) 

**Step 4 — Zero rsETH is minted when price is inflated.**

`getRsETHAmountToMint` computes:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

If `rsETHPrice` is inflated to `D + 1` (where `D` is the donation), a victim depositing `V` ETH receives `V / (D + 1)` rsETH, which truncates to `0` when `D ≥ V`. [6](#0-5) 

`_beforeDeposit` only reverts if `rsethAmountToMint < minRSETHAmountExpected`. When the victim passes `minRSETHAmountExpected = 0`, the check passes and `_mintRsETH(0)` is called — minting nothing while the victim's ETH is already held by the contract. [7](#0-6) 

### Impact Explanation

**Critical — direct theft of user funds.**

The victim's ETH is transferred into `LRTDepositPool` before any minting occurs (ETH arrives via `msg.value` in `depositETH`). If `rsethAmountToMint == 0` and `minRSETHAmountExpected == 0`, the call succeeds, the victim receives zero rsETH, and their ETH remains in the protocol. The attacker's single wei of rsETH now represents the entire protocol TVL (attacker's initial deposit + donation + victim's deposit), redeemable via the withdrawal path.

### Likelihood Explanation

**Medium.** Two conditions must hold simultaneously:

1. `pricePercentageLimit == 0` — this is the **default state** at deployment since `initialize()` never sets it. The admin must call `setPricePercentageLimit` explicitly. During the window before that call, the guard is absent.
2. The victim passes `minRSETHAmountExpected = 0` — this occurs when integrators, aggregators, or simple front-ends omit slippage protection, a common real-world pattern.

Both conditions are realistic, particularly at protocol launch.

### Recommendation

1. **Enforce a non-zero rsETH output in `_beforeDeposit`**: revert if `rsethAmountToMint == 0` regardless of `minRSETHAmountExpected`.
2. **Set `pricePercentageLimit` to a safe value inside `initialize()`** (e.g., 1% = `1e16`) so the guard is active from block 0.
3. **Restrict the `receive()` function** or add a separate accounting variable for "legitimate" ETH inflows so that arbitrary donations are not counted as protocol TVL.
4. Consider minting a small amount of rsETH to a dead address on first deposit (dead-shares pattern) to prevent the price from being manipulated from a supply of 1 wei.

### Proof of Concept

```
Initial state: rsethSupply = 0, pricePercentageLimit = 0

1. Attacker calls depositETH{value: 1 wei}(0, "")
   → rsETHPrice = 1e18 (hardcoded when supply == 0)
   → rsethAmountToMint = (1 * 1e18) / 1e18 = 1
   → Attacker receives 1 wei rsETH

2. Attacker sends 1e18 ETH to LRTDepositPool via receive()
   → address(this).balance = 1 + 1e18

3. Attacker calls updateRSETHPrice()
   → totalETHInProtocol = 1 + 1e18
   → newRsETHPrice = (1 + 1e18) / 1 ≈ 1e18 * 1e18  (in wei units: ~1e18+1)
   → pricePercentageLimit == 0 → guard skipped → rsETHPrice updated

4. Victim calls depositETH{value: 1e18}(0, "")
   → rsethAmountToMint = (1e18 * 1e18) / (1e18 + 1) = 0  (integer truncation)
   → minRSETHAmountExpected = 0 → check passes
   → _mintRsETH(0) → victim receives 0 rsETH
   → victim's 1e18 ETH is now in the contract

5. Protocol state:
   → totalETHInProtocol ≈ 2e18 + 1 wei
   → rsethSupply = 1 wei (attacker only)
   → Attacker's 1 wei rsETH is worth ≈ 2e18 ETH

6. Attacker initiates withdrawal → recovers ~2e18 ETH
   Net profit: ~1e18 ETH (the victim's entire deposit)
```

### Citations

**File:** contracts/LRTDepositPool.sol (L58-67)
```text
    receive() external payable { }

    /// @dev receive from RewardReceiver
    function receiveFromRewardReceiver() external payable { }

    /// @dev receive from LRTConverter
    function receiveFromLRTConverter() external payable { }

    /// @dev receive from NodeDelegator
    function receiveFromNodeDelegator() external payable { }
```

**File:** contracts/LRTDepositPool.sol (L385-397)
```text
    function getTotalAssetDeposits(address asset) public view override returns (uint256 totalAssetDeposit) {
        (
            uint256 assetLyingInDepositPool,
            uint256 assetLyingInNDCs,
            uint256 assetStakedInEigenLayer,
            uint256 assetUnstakingFromEigenLayer,
            uint256 assetLyingInConverter,
            uint256 assetLyingUnstakingVault
        ) = getAssetDistributionData(asset);
        uint256 effectiveAssetWithEigenLayer = assetStakedInEigenLayer + assetUnstakingFromEigenLayer;
        return (assetLyingInDepositPool + assetLyingInNDCs + effectiveAssetWithEigenLayer + assetLyingInConverter
                + assetLyingUnstakingVault);
    }
```

**File:** contracts/LRTDepositPool.sol (L480-480)
```text
        ethLyingInDepositPool = address(this).balance;
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
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

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
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
