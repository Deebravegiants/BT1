### Title
Publicly Callable `updateRSETHPrice()` Enables Sandwich Attack to Steal Staking Yield from rsETH Holders - (`contracts/LRTOracle.sol`)

### Summary

`LRTOracle.updateRSETHPrice()` is publicly callable by any address. Because both the deposit (`LRTDepositPool.depositETH`) and instant withdrawal (`LRTWithdrawalManager.instantWithdrawal`) functions price rsETH using the stored `rsETHPrice` state variable, an attacker can deposit at a stale (lower) price, trigger the price update themselves, and immediately withdraw at the higher price — extracting staking yield that belongs to existing rsETH holders.

### Finding Description

`updateRSETHPrice()` is declared `public` with no access restriction:

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

The stored `rsETHPrice` is only updated when this function is called. Between calls, staking rewards accumulate in EigenLayer, causing the true NAV of rsETH to exceed the stored price. Both the deposit and instant-withdrawal paths read this stale stored value directly.

**Deposit pricing** (`LRTDepositPool.getRsETHAmountToMint`):
```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```
A lower `rsETHPrice` yields *more* rsETH for the same ETH input.

**Instant-withdrawal pricing** (`LRTWithdrawalManager.getExpectedAssetAmount`):
```solidity
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```
A higher `rsETHPrice` yields *more* ETH for the same rsETH input.

**Attack sequence (single block, when `isInstantWithdrawalEnabled[ETH]` is true):**

1. Observe that `rsETHPrice` is stale at `P1` while true value is `P2 > P1` (rewards have accrued).
2. Call `LRTDepositPool.depositETH{value: X}(...)` → receive `X * 1e18 / P1` rsETH (more than fair share).
3. Approve `LRTWithdrawalManager` to burn the received rsETH.
4. Call `LRTOracle.updateRSETHPrice()` → `rsETHPrice` updates to `P2`.
5. Call `LRTWithdrawalManager.instantWithdrawal(ETH, rsETHAmount, ...)` → receive `rsETHAmount * P2 / 1e18` ETH.
6. Net profit: `X * (P2/P1 - 1)` ETH, minus `instantWithdrawalFee`.

The same attack works via the standard `initiateWithdrawal` path (steps 1–4 then `initiateWithdrawal` at the new price), locking in the inflated `expectedAssetAmount` before the 8-day delay, at the cost of price risk during the delay window.

The attack is also executable as a classic mempool sandwich: front-run any pending `updateRSETHPrice()` call with a deposit, let the price update land, then back-run with an instant withdrawal.

### Impact Explanation

The attacker extracts staking rewards that accrued to existing rsETH holders. Each unit of yield captured by the attacker is a unit not reflected in the NAV of honest holders' rsETH. This is direct theft of unclaimed yield from all existing rsETH holders, proportional to the price gap `P2 - P1` and the attack size.

### Likelihood Explanation

- `updateRSETHPrice()` is unconditionally public; any EOA or contract can call it.
- Staking rewards accrue continuously; the price is always stale between oracle updates.
- The instant-withdrawal path (`isInstantWithdrawalEnabled`) is a live, configurable feature.
- The `pricePercentageLimit` guard only reverts non-manager callers when the increase exceeds the configured threshold; if `pricePercentageLimit == 0` (unset) there is no cap at all.
- Even with a 1 % `pricePercentageLimit`, a sufficiently large deposit makes the attack profitable after the `instantWithdrawalFee`.

### Recommendation

1. **Restrict `updateRSETHPrice()`** to an authorized role (manager/operator/keeper), removing the public entry point that lets attackers time the update.
2. **Alternatively**, call `_updateRsETHPrice()` at the start of every `depositETH`, `depositAsset`, and `instantWithdrawal` execution so the price is always fresh before amounts are calculated — eliminating the stale-price window.
3. **Ensure** `instantWithdrawalFee` is always set above the maximum per-call price increase permitted by `pricePercentageLimit` as a secondary defence.

### Proof of Concept

```
State: rsETHPrice = 1.05e18, true value = 1.06e18 (rewards accrued, not yet updated)

Attacker contract (single tx):
  1. depositETH{value: 1e18}()
     → rsETHMinted = 1e18 * 1e18 / 1.05e18 = 952_380_952_380_952_380

  2. rsETH.approve(withdrawalManager, 952_380_952_380_952_380)

  3. lrtOracle.updateRSETHPrice()
     → rsETHPrice = 1.06e18

  4. withdrawalManager.instantWithdrawal(ETH, 952_380_952_380_952_380, "")
     → assetAmountUnlocked = 952_380_952_380_952_380 * 1.06e18 / 1e18
                           = 1_009_523_809_523_809_523 wei (~1.0095 ETH)

Net gain: ~9_523_809_523_809_523 wei (~0.0095 ETH, ~0.95%) per 1 ETH deposited,
minus instantWithdrawalFee.
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L252-266)
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
```

**File:** contracts/LRTDepositPool.sol (L516-521)
```text
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L212-253)
```text
    function instantWithdrawal(
        address asset,
        uint256 rsETHUnstaked,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedAsset(asset)
        onlySupportedStrategy(asset)
        onlyInstantWithdrawalAllowed(asset)
    {
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }
        if (IERC20(lrtConfig.rsETH()).balanceOf(msg.sender) < rsETHUnstaked) revert NotEnoughRsETH();
        uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
        IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
        ILRTUnstakingVault unstakingVault = ILRTUnstakingVault(lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT));
        if (assetAmountUnlocked > unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)) {
            revert CantInstantWithdrawMoreThanAvailable();
        }

        unstakingVault.redeem(asset, assetAmountUnlocked);

        uint256 fee = (assetAmountUnlocked * instantWithdrawalFee) / 10_000;
        uint256 userAmount = assetAmountUnlocked - fee;

        address feeRecipient = instantWithdrawalFeeRecipient;
        if (feeRecipient == address(0)) {
            // Backwards-compatible default: send fees to the protocol treasury
            feeRecipient = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
        }
        if (fee > 0) {
            _transferAsset(asset, feeRecipient, fee);
            emit InstantWithdrawalFeeCollected(msg.sender, asset, fee);
        }

        _transferAsset(asset, msg.sender, userAmount);
        emit ReferralIdEmitted(referralId);
        emit AssetWithdrawalFinalized(msg.sender, asset, rsETHUnstaked, userAmount);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L580-594)
```text
    function getExpectedAssetAmount(
        address asset,
        uint256 amount
    )
        public
        view
        override
        returns (uint256 underlyingToReceive)
    {
        // setup oracle contract
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```
