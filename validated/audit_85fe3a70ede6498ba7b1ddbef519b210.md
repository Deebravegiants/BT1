### Title
`FeeReceiver.sendFunds()` Has No Access Control, Allowing Anyone to Force MEV Reward Distribution and Steal Unclaimed Yield - (File: contracts/FeeReceiver.sol)

### Summary
The `sendFunds()` function in `FeeReceiver.sol` is callable by any address with no role restriction. This allows an attacker to force the transfer of accumulated MEV/EL rewards from the `FeeReceiver` into the `LRTDepositPool` at a self-chosen moment, artificially inflating the rsETH price, and then immediately withdraw at the inflated price — capturing yield that was earned before they held rsETH.

### Finding Description
`FeeReceiver` is the protocol's MEV and execution-layer reward receiver contract. Its `sendFunds()` function is intended to be called by a privileged manager to move accumulated ETH rewards into the deposit pool at an appropriate time. However, the function carries no access control modifier:

```solidity
// contracts/FeeReceiver.sol line 53
function sendFunds() external {
    uint256 balance = address(this).balance;
    ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();
    emit MevRewardsAddedToTVL(balance);
}
``` [1](#0-0) 

In contrast, every other state-changing function in the same contract is gated behind `onlyRole(LRTConstants.MANAGER)`:

```solidity
// contracts/FeeReceiver.sol line 66
function setDepositPool(address _depositPool) external onlyRole(LRTConstants.MANAGER) { ... }
``` [2](#0-1) 

The `FeeReceiver` balance is **not** counted in the TVL until `sendFunds()` is called. The `getETHDistributionData()` function in `LRTDepositPool` explicitly documents this:

```solidity
/// @dev rewards are not accounted here
/// it will automatically be accounted once it is moved from feeReceiver/rewardReceiver to depositPool
``` [3](#0-2) 

This means the rsETH price (computed from TVL / rsETH supply) is lower while rewards sit in `FeeReceiver`, and jumps upward the moment `sendFunds()` is called.

### Impact Explanation
**High — Theft of unclaimed yield.**

An attacker can execute the following sandwich:

1. Observe that `FeeReceiver` has accumulated a significant ETH balance (MEV/EL rewards not yet in TVL).
2. Buy rsETH at the current (lower) price, which does not yet reflect the pending rewards.
3. Call `sendFunds()` — permissionless — to push all accumulated rewards into `LRTDepositPool`, immediately increasing the rsETH price.
4. Call `instantWithdrawal()` (when enabled) or `initiateWithdrawal()` at the now-inflated rsETH price, locking in the higher expected asset amount.
5. Receive more underlying assets than the rsETH was worth at purchase time, capturing yield that was earned by the protocol before the attacker held any rsETH.

The profit equals `(MEV rewards in FeeReceiver) × (attacker rsETH / total rsETH supply)` — extracted from rewards that pre-dated the attacker's position. [4](#0-3) 

The `getExpectedAssetAmount` used at withdrawal initiation time is:

```solidity
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
``` [5](#0-4) 

Because `rsETHPrice()` reflects the inflated TVL after `sendFunds()`, the attacker locks in the higher payout.

### Likelihood Explanation
**Medium.** The attack requires no special privileges — only the ability to hold rsETH and call a public function. MEV/EL rewards accumulate continuously in `FeeReceiver`, so the opportunity recurs regularly. The attacker only needs to monitor the `FeeReceiver` balance on-chain and execute the three-step sequence atomically or in rapid succession. No governance capture, key compromise, or external dependency is required.

### Recommendation
Add an access control modifier to `sendFunds()` so that only the `MANAGER` role (or a designated operator role) can trigger reward distribution:

```solidity
function sendFunds() external onlyRole(LRTConstants.MANAGER) {
    uint256 balance = address(this).balance;
    ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();
    emit MevRewardsAddedToTVL(balance);
}
```

This is consistent with the access control pattern already applied to `setDepositPool()` in the same contract.

### Proof of Concept

```
// Setup: FeeReceiver holds 50 ETH in accumulated MEV rewards (not in TVL)
// rsETH price = 1.0 ETH/rsETH (TVL = 1000 ETH, supply = 1000 rsETH)

// Step 1: Attacker deposits 100 ETH → receives 100 rsETH at price 1.0
lrtDepositPool.depositETH{value: 100 ether}(minRsETH, "");

// Step 2: Attacker calls sendFunds() — no access control, succeeds
feeReceiver.sendFunds();
// FeeReceiver's 50 ETH moves to DepositPool
// New TVL = 1150 ETH, supply = 1100 rsETH → rsETH price ≈ 1.0454 ETH/rsETH

// Step 3: Attacker initiates withdrawal of 100 rsETH
// expectedAssetAmount = 100 * 1.0454 = 104.54 ETH (locked at inflated price)
lrtWithdrawalManager.initiateWithdrawal(ETH_TOKEN, 100e18, "");

// Step 4: After delay, attacker completes withdrawal and receives ~104.54 ETH
// Profit: ~4.54 ETH captured from MEV rewards earned before attacker held rsETH
``` [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/FeeReceiver.sol (L52-58)
```text
    /// @dev send all rewards to deposit pool
    function sendFunds() external {
        uint256 balance = address(this).balance;
        ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();

        emit MevRewardsAddedToTVL(balance);
    }
```

**File:** contracts/FeeReceiver.sol (L66-72)
```text
    function setDepositPool(address _depositPool) external onlyRole(LRTConstants.MANAGER) {
        if (_depositPool == address(0)) revert InvalidEmptyValue();

        depositPool = _depositPool;

        emit DepositPoolSet(_depositPool);
    }
```

**File:** contracts/LRTDepositPool.sol (L61-61)
```text
    function receiveFromRewardReceiver() external payable { }
```

**File:** contracts/LRTDepositPool.sol (L464-467)
```text
    /// @dev provides ETH amount distribution data among depositPool, NDCs and eigenLayer
    /// @dev rewards are not accounted here
    /// it will automatically be accounted once it is moved from feeReceiver/rewardReceiver to depositPool
    function getETHDistributionData()
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

**File:** contracts/LRTWithdrawalManager.sol (L590-594)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```
