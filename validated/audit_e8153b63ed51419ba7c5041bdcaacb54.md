### Title
Stale `rsETHPrice` in `instantWithdrawal` Allows Users to Exit at Above-Market Rate, Forcing Losses on Remaining rsETH Holders - (File: contracts/LRTWithdrawalManager.sol)

---

### Summary

The `instantWithdrawal` function in `LRTWithdrawalManager` computes the user's payout using the stored `rsETHPrice` from `LRTOracle` without first refreshing it. Because `rsETHPrice` is a cached value updated only on explicit calls to `updateRSETHPrice()`, a window exists where the stored price is higher than the true protocol value. A user who monitors LST oracle prices can call `instantWithdrawal` during this window — before `updateRSETHPrice()` is called — and receive more underlying assets than their rsETH is actually worth. The remaining rsETH holders absorb the resulting shortfall when the price is eventually updated.

---

### Finding Description

**Root cause 1 — `rsETHPrice` is a stale cached value.**

`LRTOracle` stores `rsETHPrice` as a state variable that is only updated when `updateRSETHPrice()` (or `updateRSETHPriceAsManager()`) is explicitly called. [1](#0-0) [2](#0-1) 

Between calls, the actual ETH value of the protocol can change (LST depeg, EigenLayer slashing) while `rsETHPrice` remains at the old, higher value.

**Root cause 2 — `instantWithdrawal` reads the stale price directly.**

`getExpectedAssetAmount` computes the payout as:

```
underlyingToReceive = rsETHUnstaked * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset)
``` [3](#0-2) 

`lrtOracle.rsETHPrice()` is the stale cached value; `lrtOracle.getAssetPrice(asset)` reads the live oracle price. If the LST has depegged, `getAssetPrice(asset)` is already lower, but `rsETHPrice` has not yet been reduced to match. The division therefore yields a larger-than-correct asset amount.

`instantWithdrawal` calls `getExpectedAssetAmount` without first calling `updateRSETHPrice()`: [4](#0-3) 

**Concrete example.**

Assume the protocol holds 100 stETH, rsETH supply = 100, and stETH depegs from 1.00 ETH to 0.95 ETH:

| State | `rsETHPrice` (stored) | `getAssetPrice(stETH)` (live) |
|---|---|---|
| Before depeg | 1.00 ETH | 1.00 ETH |
| After depeg, before update | 1.00 ETH (stale) | 0.95 ETH |

A savvy user burns 10 rsETH via `instantWithdrawal`:
- Payout = `10 * 1.00 / 0.95` = **10.526 stETH** (worth 10.00 ETH at current price)
- Actual fair value of 10 rsETH = 10 × 0.95 = **9.50 ETH**
- **Excess extracted: ~0.50 ETH**

After the exit, the remaining 90 rsETH holders share 89.474 stETH (worth 84.99 ETH) instead of the 85.50 ETH they are entitled to. When `updateRSETHPrice()` is called, the price drops further than it should, and the shortfall is borne entirely by the remaining holders.

**This is not MEV-dependent.** The attacker simply monitors the live LST oracle price (e.g., via `lrtOracle.getAssetPrice(stETH)`) and calls `instantWithdrawal` before anyone calls `updateRSETHPrice()`. The attack works on any chain and does not require mempool access.

**Contrast with `initiateWithdrawal`.**

The queued withdrawal path is not exploitable in the same way because `_calculatePayoutAmount` caps the payout at the *minimum* of the originally expected amount and the current return at unlock time: [5](#0-4) 

If the price drops before `unlockQueue` is called, the user receives the lower current return. `instantWithdrawal` has no such protection.

---

### Impact Explanation

**High — Theft of unclaimed yield / value from remaining rsETH holders.**

Every user who exits via `instantWithdrawal` during the stale-price window extracts more underlying assets than their rsETH entitles them to. The deficit is silently transferred to all remaining rsETH holders, who receive a lower price when `updateRSETHPrice()` is eventually called. The economic incentive is to exit before the price update and re-enter afterward at the lower price, compounding the loss for passive holders. This is structurally identical to the Dopex H-02 pattern.

---

### Likelihood Explanation

**Medium.**

- `instantWithdrawal` must be enabled per asset (`isInstantWithdrawalEnabled[asset]`), which is a manager decision. When enabled, the attack surface is open.
- The `LRTUnstakingVault` must hold sufficient assets (`getAssetsAvailableForInstantWithdrawal`). In normal operation this is expected to be non-zero.
- LST depegs (stETH, ETHx) and EigenLayer slashing events are realistic triggers. The price-update window can span minutes to hours depending on bot cadence.
- No special technical skill is required beyond monitoring `lrtOracle.getAssetPrice(asset)` on-chain. [6](#0-5) [7](#0-6) 

---

### Recommendation

Before computing the payout in `instantWithdrawal`, force a price refresh:

```solidity
// At the top of instantWithdrawal, before getExpectedAssetAmount:
ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE)).updateRSETHPrice();
```

Alternatively, compute the payout directly from live oracle prices rather than the cached `rsETHPrice`, mirroring the logic inside `_updateRsETHPrice`. This eliminates the stale-price window entirely.

A secondary mitigation is to add a withdrawal cooldown (analogous to the Dopex recommendation) so that users cannot deposit rsETH and immediately call `instantWithdrawal` in the same block, preventing atomic round-trip exploitation.

---

### Proof of Concept

```
1. Protocol state: 100 stETH held, rsETH supply = 100, rsETHPrice = 1.00 ETH (stored).
2. stETH depegs: live oracle now returns 0.95 ETH for stETH.
   rsETHPrice has NOT been updated yet.
3. Attacker (Bob) calls instantWithdrawal(stETH, 10e18, ""):
   - assetAmountUnlocked = 10e18 * 1.00e18 / 0.95e18 = 10.526e18 stETH
   - Bob burns 10 rsETH, receives 10.526 stETH (worth 10.00 ETH at current price)
   - Fair value of 10 rsETH = 9.50 ETH → Bob extracted 0.50 ETH excess
4. updateRSETHPrice() is called:
   - totalETH = 89.474 stETH * 0.95 = 84.99 ETH
   - rsETH supply = 90
   - new rsETHPrice = 84.99 / 90 = 0.9443 ETH  (should be 0.95 ETH)
5. Dave (passive holder, 10 rsETH) now holds rsETH worth 9.443 ETH instead of 9.50 ETH.
   Dave absorbed Bob's excess extraction.
``` [4](#0-3) [3](#0-2) [8](#0-7)

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

**File:** contracts/LRTOracle.sol (L214-250)
```text
    function _updateRsETHPrice() internal {
        address rsETHTokenAddress = lrtConfig.rsETH();
        uint256 rsethSupply = IRSETH(rsETHTokenAddress).totalSupply();

        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }

        if (highestRsethPrice == 0) {
            highestRsethPrice = rsETHPrice;
        }

        uint256 previousPrice = rsETHPrice;

        // get total ETH in the protocol (normalized to 1e18)
        uint256 totalETHInProtocol = _getTotalEthInProtocol();

        // calculate previousTVL using rsethSupply multiplied by rsETHPrice
        uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);

        IPausable lrtDepositPool = IPausable(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable withdrawalManager = IPausable(lrtConfig.getContract(LRTConstants.LRT_WITHDRAW_MANAGER));

        // determine if the protocol is active (not paused)
        bool protocolPaused = lrtDepositPool.paused() || withdrawalManager.paused() || paused;

        // only take fee if TVL increased and protocol is not paused
        uint256 protocolFeeInETH = 0;
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTWithdrawalManager.sol (L78-80)
```text
    modifier onlyInstantWithdrawalAllowed(address asset) {
        if (!isInstantWithdrawalEnabled[asset]) revert InstantWithdrawalNotEnabled();
        _;
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

**File:** contracts/LRTWithdrawalManager.sol (L580-593)
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

**File:** contracts/LRTUnstakingVault.sol (L229-238)
```text
    function getAssetsAvailableForInstantWithdrawal(address asset)
        external
        view
        onlySupportedAsset(asset)
        returns (uint256 availableAmount)
    {
        uint256 vaultBalance = balanceOf(asset);
        uint256 reservedBuffer = queuedWithdrawalsBuffer[asset];
        availableAmount = reservedBuffer >= vaultBalance ? 0 : vaultBalance - reservedBuffer;
    }
```
