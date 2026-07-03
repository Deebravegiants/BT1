### Title
Stale Oracle Rate Enables Yield Theft via Deposit-then-InstantWithdrawal - (File: contracts/LRTWithdrawalManager.sol)

### Summary
`LRTOracle.updateRSETHPrice()` is a publicly callable, manually-invoked function. Between oracle updates, `rsETHPrice` is stale. An unprivileged attacker can deposit ETH at the stale (lower) rate, trigger the oracle update themselves, and immediately redeem via `LRTWithdrawalManager.instantWithdrawal()` at the newly updated (higher) rate, extracting the accrued yield that belongs to existing rsETH holders.

### Finding Description
`LRTOracle.updateRSETHPrice()` is declared `public` with no access restriction:

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

`LRTDepositPool.depositETH()` mints rsETH using the stored `rsETHPrice` at the moment of deposit:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

`LRTWithdrawalManager.instantWithdrawal()` computes the payout using the **current** `rsETHPrice` at the moment of withdrawal, with no locking or delay:

```solidity
uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
// getExpectedAssetAmount: amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset)
```

Because `instantWithdrawal` reads the live oracle price at execution time (unlike the queued withdrawal path, which caps payout at the initiation-time expected amount via `_calculatePayoutAmount`), the deposit and withdrawal legs use **different** oracle prices whenever the attacker triggers an oracle update between them.

The queued withdrawal path is protected: `_calculatePayoutAmount` returns `min(expectedAssetAmount, currentReturn)`, so a price increase after initiation does not benefit the withdrawer. `instantWithdrawal` has no equivalent protection.

### Impact Explanation
Every time rewards accrue and `rsETHPrice` lags behind the true value, an attacker can atomically:
1. Deposit at the stale rate (receiving more rsETH than fair value).
2. Call `updateRSETHPrice()` to advance the price.
3. Instantly redeem at the new rate.

The profit equals `(newPrice − oldPrice) × depositAmount / newPrice`, minus the `instantWithdrawalFee`. This profit is extracted directly from the yield that should have been distributed pro-rata to all existing rsETH holders, constituting theft of unclaimed yield.

### Likelihood Explanation
- `updateRSETHPrice()` is callable by any address with no role restriction.
- `instantWithdrawal` is enabled per-asset by the manager (`isInstantWithdrawalEnabled[asset]`); when enabled, the path is fully permissionless for any rsETH holder.
- The oracle is updated periodically (not on every block), so stale windows exist regularly.
- The attack requires no front-running: the attacker controls all three steps (deposit → oracle update → instant withdrawal) in consecutive transactions.
- Profitability requires `instantWithdrawalFee` to be below the accrued yield percentage. At typical LRT reward rates (~4–6% APY, ~0.01% per day) and a fee of 0–50 bps, the attack is profitable on any day the fee is below the daily yield.

### Recommendation
1. **Snapshot the oracle price at deposit time** and use that snapshot as the ceiling for `instantWithdrawal` payout for the same depositor within the same oracle epoch, or
2. **Impose a minimum holding period** (e.g., one oracle update cycle) before rsETH minted via `depositETH` is eligible for `instantWithdrawal`, or
3. **Set `instantWithdrawalFee` to a value that always exceeds the maximum possible inter-update yield**, and enforce this invariant on-chain, or
4. **Restrict `updateRSETHPrice()` to a privileged role** so the attacker cannot self-trigger the price advance, reducing the attack to a front-running scenario that is harder to execute reliably.

### Proof of Concept
Preconditions: `isInstantWithdrawalEnabled[ETH] = true`, `instantWithdrawalFee = 10` bps (0.1%), rewards have accrued such that the true rsETH price is 1.001e18 but the stored `rsETHPrice` is still 1.000e18.

```
Step 1 — Deposit at stale rate:
  LRTDepositPool.depositETH{value: 1_000 ether}(minRSETH=999e18, "")
  rsethAmountToMint = 1000e18 * 1e18 / 1.000e18 = 1000e18 rsETH minted to attacker

Step 2 — Advance oracle:
  LRTOracle.updateRSETHPrice()
  rsETHPrice now = 1.001e18

Step 3 — Instant withdrawal:
  LRTWithdrawalManager.instantWithdrawal(ETH, 1000e18, "")
  assetAmountUnlocked = 1000e18 * 1.001e18 / 1e18 = 1001 ETH
  fee = 1001 * 10 / 10_000 = 1.001 ETH
  userAmount = 1001 - 1.001 = 999.999 ETH

Net result:
  Attacker spent 1000 ETH, received 999.999 ETH → net loss of 0.001 ETH at 10 bps fee.
  At fee = 0 bps: attacker receives 1001 ETH → net profit of 1 ETH.
  At fee = 5 bps: assetAmountUnlocked = 1001, fee = 0.5005 ETH, userAmount = 1000.4995 ETH → profit ≈ 0.5 ETH.
```

The attack is profitable whenever `instantWithdrawalFee (bps) < oracle_lag_yield_bps`. At typical daily LRT yields of ~1–2 bps and fees below that threshold, the attack extracts yield from all existing rsETH holders on every oracle update cycle.

**Relevant code references:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTDepositPool.sol (L515-521)
```text
        // setup oracle contract
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

**File:** contracts/LRTWithdrawalManager.sol (L824-835)
```text
    function _calculatePayoutAmount(
        WithdrawalRequest storage request,
        uint256 rsETHPrice,
        uint256 assetPrice
    )
        private
        view
        returns (uint256)
    {
        uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
        return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
    }
```
