### Title
Sandwich Attack on `updateRSETHPrice()` Allows Theft of Accrued Yield from Existing rsETH Holders - (File: contracts/LRTOracle.sol, contracts/LRTDepositPool.sol, contracts/LRTWithdrawalManager.sol)

---

### Summary

`LRTOracle.rsETHPrice` is a stored, lazily-updated value. `updateRSETHPrice()` is a public function callable by anyone. Because deposits and withdrawals both price rsETH against this stored value, an attacker can sandwich a price update — depositing at the stale (lower) price, triggering the update, then withdrawing at the new (higher) price — to extract accrued yield that belongs to existing rsETH holders.

---

### Finding Description

`LRTOracle` stores `rsETHPrice` as a state variable that is only updated when `updateRSETHPrice()` is explicitly called. [1](#0-0) 

The update function is unrestricted — any address may call it: [2](#0-1) 

When a user deposits, `getRsETHAmountToMint()` divides by the **stored** `rsETHPrice`: [3](#0-2) 

When a user initiates a withdrawal, `getExpectedAssetAmount()` multiplies by the **stored** `rsETHPrice`: [4](#0-3) 

The `expectedAssetAmount` is locked in at `initiateWithdrawal()` time and stored in the withdrawal request: [5](#0-4) 

**Attack sequence (standard withdrawal path):**

1. EigenLayer staking rewards accrue (e.g., ETH pod rewards, LST rebases), but `rsETHPrice` has not been updated — it is stale and lower than the true value.
2. Attacker deposits a large amount of ETH/LST at the stale low price. Because `rsethAmountToMint = depositAmount / staleLowPrice`, the attacker receives **more rsETH than their proportional share** of the protocol's actual TVL.
3. Attacker calls `updateRSETHPrice()`. The price rises to reflect the accrued rewards, but the attacker's extra rsETH dilutes the price increase for existing holders.
4. Attacker calls `initiateWithdrawal()`. The `expectedAssetAmount` is now computed at the updated higher price, locking in a profit.
5. After the 8-day delay, attacker calls `completeWithdrawal()` and receives more assets than deposited.

**Attack sequence (instant withdrawal path — no delay):**

If `isInstantWithdrawalEnabled[asset]` is true, steps 4–5 collapse into a single `instantWithdrawal()` call with no waiting period: [6](#0-5) 

**Numerical example:**

- Protocol state: `totalETH = 1000 ETH`, `rsethSupply = 1000`, `rsETHPrice = 1.0 ETH` (stale; true price should be `1.01 ETH` due to 10 ETH accrued rewards).
- Attacker deposits `10,000 ETH` at stale price `1.0` → receives `10,000 rsETH`.
- Attacker calls `updateRSETHPrice()`. New price = `(1000 + 10 + 10,000) / (1000 + 10,000)` ≈ `1.0009 ETH`.
- Attacker withdraws `10,000 rsETH` at `1.0009` → receives `10,009 ETH`.
- Attacker profit: `~9 ETH` (≈ 90% of the 10 ETH that belonged to existing holders).

The larger the attacker's deposit relative to the existing TVL, the greater the fraction of accrued rewards they capture.

---

### Impact Explanation

Existing rsETH holders lose a portion of their accrued yield. The attacker extracts value that was earned by long-term stakers through EigenLayer restaking rewards and LST rebases. This is a direct theft of unclaimed yield.

**Impact: High — Theft of unclaimed yield.**

---

### Likelihood Explanation

- `updateRSETHPrice()` is public and permissionless; no special role is needed.
- `depositETH()` / `depositAsset()` are standard user-facing functions.
- The price update cadence is off-chain / keeper-driven, meaning windows of staleness are routine and predictable by monitoring on-chain state.
- The attacker only needs capital (which can be flash-loaned for the deposit, though the withdrawal delay complicates flash-loan use for the standard path; instant withdrawal removes this constraint entirely).
- No governance capture, oracle manipulation, or admin collusion is required.

**Likelihood: Medium** (requires capital and timing, but the entry path is fully permissionless and the staleness window is a normal operating condition).

---

### Recommendation

1. **Call `updateRSETHPrice()` atomically inside `depositETH()` / `depositAsset()` before computing `getRsETHAmountToMint()`**, so deposits always price against the freshest TVL. This mirrors the recommendation in the external report to call the reward-update function before any share-issuance or redemption.
2. **Alternatively, enforce a deposit lock-up or snapshot mechanism** so that rsETH minted in block N cannot be used to initiate a withdrawal until at least one price update has occurred after block N.
3. For the instant withdrawal path, ensure `updateRSETHPrice()` is called atomically within `instantWithdrawal()` before computing `getExpectedAssetAmount()`.

---

### Proof of Concept

```
// Pseudocode — all calls in one transaction (instant withdrawal) or across blocks (standard)

// Step 1: Observe rsETHPrice is stale (lower than true value)
uint256 stalePrice = lrtOracle.rsETHPrice(); // e.g., 1.000e18

// Step 2: Deposit large amount at stale price
lrtDepositPool.depositETH{value: 10_000 ether}(0, "");
// Attacker receives 10_000e18 / 1.000e18 = 10_000 rsETH
// (true price 1.010e18 would have given only ~9901 rsETH)

// Step 3: Trigger price update — permissionless
lrtOracle.updateRSETHPrice();
// rsETHPrice now reflects accrued rewards, e.g., 1.0009e18

// Step 4a (instant withdrawal, if enabled):
lrtWithdrawalManager.instantWithdrawal(ETH_TOKEN, 10_000e18, "");
// Receives 10_000 * 1.0009 = 10_009 ETH — profit of ~9 ETH stolen from existing holders

// Step 4b (standard withdrawal):
lrtWithdrawalManager.initiateWithdrawal(ETH_TOKEN, 10_000e18, "");
// expectedAssetAmount locked at 10_009 ETH
// ... wait withdrawalDelayBlocks (~8 days) ...
lrtWithdrawalManager.completeWithdrawal(ETH_TOKEN, "");
// Receives 10_009 ETH
``` [2](#0-1) [7](#0-6) [8](#0-7) [9](#0-8)

### Citations

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

**File:** contracts/LRTWithdrawalManager.sol (L150-178)
```text
    function initiateWithdrawal(
        address asset,
        uint256 rsETHUnstaked,
        string calldata referralId
    )
        external
        override
        nonReentrant
        whenNotPaused
        onlySupportedAsset(asset)
        onlySupportedStrategy(asset)
    {
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }

        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);

        emit ReferralIdEmitted(referralId);
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

**File:** contracts/LRTWithdrawalManager.sol (L590-593)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```
