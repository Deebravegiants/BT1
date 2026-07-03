### Title
Stale `rsETHPrice` in `LRTOracle` Allows Depositors to Extract Accumulated Yield Before Price Update — (`contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle.rsETHPrice` is a stored/cached value that is only updated when `updateRSETHPrice()` is explicitly called. Because `updateRSETHPrice()` carries **no access control** (it is `public`), an attacker can deposit at the stale (lower) price, immediately trigger the price update themselves, and then initiate a withdrawal at the freshly updated (higher) price — extracting the accumulated staking yield that belongs to existing depositors.

---

### Finding Description

`LRTOracle` stores the rsETH/ETH exchange rate in a state variable `rsETHPrice`. [1](#0-0) 

This value is **not** recalculated on every deposit or withdrawal. It is only updated when `updateRSETHPrice()` is called: [2](#0-1) 

Critically, `updateRSETHPrice()` is declared `public` with no role restriction — any externally owned account can call it at any time.

Both the deposit and withdrawal paths consume this stored value directly.

**Deposit** (`LRTDepositPool.getRsETHAmountToMint`):

```
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [3](#0-2) 

A **lower** (stale) `rsETHPrice` causes the division to yield a **larger** rsETH mint amount — the depositor receives more shares than the current fair value warrants.

**Withdrawal** (`LRTWithdrawalManager.getExpectedAssetAmount`):

```
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
``` [4](#0-3) 

A **higher** (freshly updated) `rsETHPrice` causes the multiplication to yield a **larger** asset payout — the withdrawer receives more ETH/LST than they deposited.

The combination of these two facts creates the exploit window: deposit at the stale price, update the price, withdraw at the updated price.

The `_updateRsETHPrice` internal function computes the new price from the live TVL of all supported assets and the current rsETH total supply: [5](#0-4) 

As EigenLayer staking rewards accrue, the TVL grows while `rsETHPrice` remains frozen at its last stored value. The gap between the stale stored price and the true price is the attacker's extractable profit.

---

### Impact Explanation

The attacker mints rsETH at a price that does not yet reflect accumulated staking rewards, then redeems at the price that does. The difference is yield that was earned by existing long-term depositors but is now diverted to the attacker. This is a direct, quantifiable theft of unclaimed yield from protocol participants.

**Impact: High — Theft of unclaimed yield.**

---

### Likelihood Explanation

- `updateRSETHPrice()` is `public` with no access control; the attacker controls exactly when the price update fires.
- All inputs to the price calculation (`getTotalAssetDeposits`, underlying LST oracle prices, rsETH total supply) are on-chain and publicly readable, so the attacker can compute the exact profit before committing.
- The attack requires no privileged role, no governance capture, and no external protocol compromise.
- The only partial mitigations are `pricePercentageLimit` (which can be zero, and which only caps a single update — not the cumulative drift) and the 8-day withdrawal delay (which adds holding-period risk but does not prevent the attack, especially when `instantWithdrawal` is enabled for an asset).

**Likelihood: Medium.**

---

### Recommendation

1. **Call `updateRSETHPrice()` atomically inside `depositETH`/`depositAsset` and `initiateWithdrawal`/`instantWithdrawal`** before computing the mint or redemption amount. This ensures the price used for every user interaction reflects the current TVL.
2. Alternatively, implement a **commit-reveal / epoch-based** deposit and withdrawal scheme: collect deposit and withdrawal requests during the current epoch and settle them all at the price computed at the start of the next epoch, so no single actor can observe the future price before committing funds.
3. Ensure `pricePercentageLimit` is always set to a non-zero value and is enforced consistently, as a defence-in-depth measure.

---

### Proof of Concept

**Setup**: Assume staking rewards have accrued since the last `updateRSETHPrice()` call. The true rsETH/ETH rate is 1.05 ETH per rsETH, but `rsETHPrice` is still stored as 1.00 ETH.

**Step 1 — Deposit at stale price.**

Attacker calls `LRTDepositPool.depositETH{value: 100 ETH}(minRSETH, "")`.

`getRsETHAmountToMint` computes:
```
rsethMinted = (100e18 * 1e18) / 1.00e18 = 100 rsETH
```
Fair value at the true rate would have been `100 / 1.05 ≈ 95.24 rsETH`. The attacker receives ~4.76 rsETH in excess. [6](#0-5) 

**Step 2 — Trigger price update.**

Attacker calls `LRTOracle.updateRSETHPrice()` (public, no access control). `rsETHPrice` is now updated to 1.05 ETH. [2](#0-1) [7](#0-6) 

**Step 3 — Initiate withdrawal at updated price.**

Attacker calls `LRTWithdrawalManager.initiateWithdrawal(ETH, 100 rsETH, "")`.

`getExpectedAssetAmount` computes:
```
underlyingToReceive = 100e18 * 1.05e18 / 1e18 = 105 ETH
```

The attacker deposited 100 ETH and will receive 105 ETH — a risk-free 5 ETH profit extracted from existing depositors' accumulated yield. [8](#0-7) [9](#0-8) 

**Step 4 — Complete withdrawal.**

After `withdrawalDelayBlocks` (≈ 8 days), attacker calls `completeWithdrawal` and receives 105 ETH. If `instantWithdrawal` is enabled for the asset, steps 1–4 collapse into a single block with no holding-period risk. [10](#0-9)

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

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```

**File:** contracts/LRTDepositPool.sol (L76-92)
```text
    function depositETH(
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        payable
        nonReentrant
        whenNotPaused
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
```

**File:** contracts/LRTDepositPool.sol (L519-520)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
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
