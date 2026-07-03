### Title
Permissionless `FeeReceiver.sendFunds()` Enables Reward Sniping Before rsETH Price Update — (File: contracts/FeeReceiver.sol)

---

### Summary

`FeeReceiver.sendFunds()` is permissionless and immediately transfers all accumulated MEV/execution-layer rewards into `LRTDepositPool`. Because the rsETH exchange rate stored in `LRTOracle.rsETHPrice` is only updated by a separate, also-permissionless call to `updateRSETHPrice()`, an attacker can deposit ETH at the stale (pre-reward) price, trigger the price update, and initiate a withdrawal at the inflated price — stealing a proportional share of rewards that were earned by pre-existing rsETH holders.

---

### Finding Description

**Root cause — two permissionless functions with no atomicity guarantee:**

`FeeReceiver.sendFunds()` has no access control: [1](#0-0) 

It immediately increases `address(LRTDepositPool).balance`, which is the numerator used by `LRTOracle._getTotalEthInProtocol()` when computing the new rsETH price.

`LRTOracle.updateRSETHPrice()` is also permissionless: [2](#0-1) 

The stored `rsETHPrice` is only refreshed when this function is explicitly called: [3](#0-2) 

Between the moment `sendFunds()` is called (rewards land in the pool) and the moment `updateRSETHPrice()` is called (price reflects those rewards), the stored `rsETHPrice` is stale — lower than the true value. Any deposit made in this window mints rsETH at the artificially low price, giving the depositor a larger share of the pool than they paid for.

**Price computation uses stored value, not live TVL:** [4](#0-3) 

The new price is computed only inside `_updateRsETHPrice()`. Deposit minting uses the previously stored `rsETHPrice`, so a depositor who acts between `sendFunds()` and `updateRSETHPrice()` receives more rsETH than the current TVL justifies.

**Attacker-controlled entry path (no admin required):**

1. Attacker calls `FeeReceiver.sendFunds()` — permissionless, moves accumulated rewards into the pool.
2. Attacker calls `LRTDepositPool.depositETH()` — mints rsETH at the stale price.
3. Attacker calls `LRTOracle.updateRSETHPrice()` — permissionless, price jumps to reflect the rewards.
4. Attacker calls `LRTWithdrawalManager.initiateWithdrawal()` — locks in the higher expected asset amount.
5. After `withdrawalDelayBlocks`, attacker calls `completeWithdrawal()` — receives more ETH than deposited.

If `isInstantWithdrawalEnabled` is active for the asset, steps 4–5 collapse into a single `instantWithdrawal()` call with no delay. [5](#0-4) 

---

### Impact Explanation

**High — Theft of unclaimed yield.**

Existing rsETH holders lose a portion of their accumulated MEV/execution-layer rewards proportional to the attacker's dilution of the rsETH supply. The attacker captures rewards they did not earn. The loss is permanent and scales with the size of the accumulated reward and the attacker's deposit relative to total supply.

Concrete example:
- Protocol TVL: 10 000 ETH, rsETH supply: 10 000, stored price: 1.0 ETH/rsETH.
- FeeReceiver holds 100 ETH (unreflected rewards).
- Attacker deposits 10 000 ETH → receives 10 000 rsETH at price 1.0.
- Attacker calls `sendFunds()` → pool now holds 20 100 ETH, supply 20 000 rsETH.
- Attacker calls `updateRSETHPrice()` → new price = 20 100 / 20 000 = 1.005.
- Attacker initiates withdrawal: 10 000 × 1.005 = 10 050 ETH.
- **Attacker profit: 50 ETH stolen from existing stakers** (who receive 10 050 ETH instead of 10 100 ETH).

---

### Likelihood Explanation

**Medium.** The attack requires no privileged role and no oracle manipulation. The only friction is the withdrawal delay (`withdrawalDelayBlocks`, capped at 16 days) and the capital needed to make the profit meaningful. Both barriers are overcome by a well-capitalised actor monitoring the FeeReceiver balance on-chain. If `instantWithdrawal` is enabled for any asset, the delay barrier disappears entirely. [6](#0-5) 

---

### Recommendation

1. **Restrict `sendFunds()`** to an authorized role (e.g., `MANAGER` or `OPERATOR_ROLE`) so rewards cannot be flushed into the pool by an arbitrary caller at a strategically chosen moment.
2. **Atomically update the price** inside `receiveFromRewardReceiver` (or at the end of `sendFunds()`) so the stored price always reflects the pool balance immediately after rewards land.
3. **Alternatively**, compute the rsETH mint amount from a live TVL snapshot rather than the stored `rsETHPrice`, eliminating the stale-price window entirely.

---

### Proof of Concept

```
State:
  LRTDepositPool ETH balance : 10 000 ETH
  rsETH totalSupply          : 10 000
  LRTOracle.rsETHPrice       : 1.000 ETH  (last updated T-1)
  FeeReceiver.balance        : 100 ETH    (MEV rewards, not yet flushed)

Step 1 — Attacker deposits 10 000 ETH:
  LRTDepositPool.depositETH{value: 10000 ether}(...)
  → rsETH minted = 10 000 / 1.000 = 10 000 rsETH
  Pool balance: 20 000 ETH, supply: 20 000 rsETH

Step 2 — Attacker flushes rewards:
  FeeReceiver.sendFunds()
  → 100 ETH transferred to LRTDepositPool
  Pool balance: 20 100 ETH, supply: 20 000 rsETH

Step 3 — Attacker triggers price update:
  LRTOracle.updateRSETHPrice()
  → rsETHPrice = 20 100 / 20 000 = 1.005 ETH

Step 4 — Attacker initiates withdrawal:
  LRTWithdrawalManager.initiateWithdrawal(ETH, 10 000 rsETH, ...)
  → expectedAssetAmount = 10 000 × 1.005 = 10 050 ETH  (locked in)

Step 5 — After delay, attacker completes withdrawal:
  → receives 10 050 ETH

Attacker profit : +50 ETH
Existing stakers: receive 10 050 ETH instead of 10 100 ETH (-50 ETH stolen)
``` [1](#0-0) [2](#0-1) [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/FeeReceiver.sol (L53-58)
```text
    function sendFunds() external {
        uint256 balance = address(this).balance;
        ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();

        emit MevRewardsAddedToTVL(balance);
    }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L244-250)
```text
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L313-315)
```text
        rsETHPrice = newRsETHPrice;

        emit RsETHPriceUpdate(rsETHPrice, previousPrice);
```

**File:** contracts/LRTWithdrawalManager.sol (L166-177)
```text
        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);

        emit ReferralIdEmitted(referralId);
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

**File:** contracts/LRTWithdrawalManager.sol (L338-343)
```text
    function setWithdrawalDelayBlocks(uint256 withdrawalDelayBlocks_) external onlyLRTManager {
        // Set an upper limit of no more than 16 days
        if (withdrawalDelayBlocks_ > 16 days / 12 seconds) revert ExceedWithdrawalDelay();

        withdrawalDelayBlocks = withdrawalDelayBlocks_;
        emit WithdrawalDelayBlocksUpdated(withdrawalDelayBlocks);
```
