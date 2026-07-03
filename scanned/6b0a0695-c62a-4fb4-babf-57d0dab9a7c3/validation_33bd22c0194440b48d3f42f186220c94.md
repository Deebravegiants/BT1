### Title
Sandwich Attack on Public `updateRSETHPrice()` Enables Atomic Yield Theft from rsETH Holders - (File: `contracts/LRTOracle.sol`)

---

### Summary
`LRTOracle.updateRSETHPrice()` carries no access control — it is `public` and callable by anyone. Combined with the public `LRTDepositPool.depositETH()` and `LRTWithdrawalManager.instantWithdrawal()`, an attacker can atomically: deposit at a stale (lower) rsETH price, trigger the price update, and immediately withdraw at the new higher price, stealing accrued yield from all existing rsETH holders.

---

### Finding Description

`updateRSETHPrice()` in `LRTOracle.sol` is declared `public` with no role restriction: [1](#0-0) 

It updates the stored `rsETHPrice` by reading total ETH in the protocol (including EigenLayer rewards that have accrued since the last update) and dividing by total rsETH supply: [2](#0-1) 

The deposit function in `LRTDepositPool` mints rsETH using the **currently stored** (potentially stale) `rsETHPrice`: [3](#0-2) 

The instant withdrawal function in `LRTWithdrawalManager` redeems rsETH using the **currently stored** `rsETHPrice` at the time of the call: [4](#0-3) 

Because `updateRSETHPrice()` is public, an attacker can control the exact ordering of all three operations within a single transaction or block.

---

### Impact Explanation

**High — Theft of unclaimed yield.**

When EigenLayer rewards accrue between two `updateRSETHPrice()` calls, the stored `rsETHPrice` is temporarily lower than the true value. An attacker who deposits just before the update receives more rsETH than their proportional share of the pool. After the update, that rsETH is redeemable for more ETH than was deposited, with the surplus coming directly from rewards that should have been distributed to existing holders.

Numerical example:
- Protocol: 100 ETH, 100 rsETH, stored price = 1.0 ETH/rsETH
- 10 ETH of EigenLayer rewards accrue; price not yet updated
- Attacker deposits 100 ETH at stale price → receives 100 rsETH (should receive ~90.9 rsETH at true price)
- `updateRSETHPrice()` executes: new price = 210 ETH / 200 rsETH = 1.05
- Attacker's 100 rsETH → 105 ETH via `instantWithdrawal`
- **Attacker profit: 5 ETH** (stolen from the 10 ETH of accrued rewards)
- Original holders receive 105 ETH instead of 110 ETH

The attack can be executed with a flash loan (zero personal capital required), making it risk-free.

---

### Likelihood Explanation

**Medium.** The attack requires:
1. `isInstantWithdrawalEnabled[asset]` to be `true` for the target asset — a manager-controlled flag that is expected to be enabled in normal operation.
2. The `LRTUnstakingVault` to hold sufficient liquid assets for the instant withdrawal.
3. Rewards to have accrued since the last `updateRSETHPrice()` call (routine between oracle updates).

All three conditions are expected to hold during normal protocol operation. The attack does not require mempool monitoring; the attacker can call all three functions atomically since `updateRSETHPrice()` is itself public.

Even without instant withdrawal enabled, the attack degrades to a delayed version: deposit at stale price, call `updateRSETHPrice()`, then `initiateWithdrawal()` at the new higher price. The `_calculatePayoutAmount` logic caps payout at `min(expectedAssetAmount, currentReturn)`: [5](#0-4) 

Since `expectedAssetAmount` is locked in at the new higher price at `initiateWithdrawal` time, the attacker still profits as long as the price does not fall below that level during the 8-day delay.

---

### Recommendation

Restrict `updateRSETHPrice()` to authorized callers (e.g., `onlyLRTOperator` or `onlyLRTManager`), consistent with how other sensitive state-changing oracle functions in the contract are protected: [6](#0-5) 

Alternatively, implement a commit-reveal or TWAP mechanism so that a single block's deposit cannot capture the full pending reward delta.

---

### Proof of Concept

```solidity
// Attacker contract — executes atomically in one transaction
contract Exploit {
    ILRTDepositPool depositPool = ILRTDepositPool(...);
    ILRTOracle oracle = ILRTOracle(...);
    ILRTWithdrawalManager withdrawalManager = ILRTWithdrawalManager(...);
    IRSETH rsETH = IRSETH(...);

    function attack() external payable {
        // Step 1: Flash-loan ETH (or use msg.value)
        // Step 2: Deposit at stale (lower) rsETH price
        depositPool.depositETH{value: msg.value}(0, "");

        // Step 3: Trigger price update — public, no access control
        oracle.updateRSETHPrice();
        // rsETHPrice is now higher; attacker's rsETH is worth more ETH

        // Step 4: Instant withdrawal at new higher price
        uint256 rsETHBalance = rsETH.balanceOf(address(this));
        rsETH.approve(address(withdrawalManager), rsETHBalance);
        withdrawalManager.instantWithdrawal(ETH_TOKEN, rsETHBalance, "");

        // Step 5: Repay flash loan; keep profit
        // address(this).balance > initial msg.value
    }
}
```

Entry path: `LRTOracle.updateRSETHPrice()` (public, no role check) → `LRTDepositPool.depositETH()` (public) → `LRTWithdrawalManager.instantWithdrawal()` (public when enabled). All three are externally reachable by an unprivileged caller. [1](#0-0) [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L94-96)
```text
    function updateRSETHPriceAsManager() external onlyLRTManager {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L249-251)
```text
        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

```

**File:** contracts/LRTDepositPool.sol (L76-93)
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
    }
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
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

**File:** contracts/LRTWithdrawalManager.sol (L833-834)
```text
        uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
        return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
```
