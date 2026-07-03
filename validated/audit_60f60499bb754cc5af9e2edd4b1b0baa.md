### Title
Front-Running `initiateWithdrawal` via `assetsCommitted` Inflation to DoS User Withdrawals - (File: contracts/LRTWithdrawalManager.sol)

### Summary
An attacker can front-run a victim's `initiateWithdrawal` call by submitting their own withdrawal request first, inflating `assetsCommitted[asset]` and reducing `getAvailableAssetAmount` below the victim's required threshold, causing the victim's transaction to revert with `ExceedAmountToWithdraw`. This is directly analogous to the reported pattern: a liquidity/availability check on a time-sensitive function that can be manipulated by an attacker to DoS legitimate users.

### Finding Description

`initiateWithdrawal` in `LRTWithdrawalManager` enforces an availability check before queuing a withdrawal request:

```solidity
uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);
if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();
assetsCommitted[asset] += expectedAssetAmount;
``` [1](#0-0) 

`getAvailableAssetAmount` computes:

```solidity
function getAvailableAssetAmount(address asset) public view override returns (uint256 availableAssetAmount) {
    ILRTDepositPool lrtDepositPool = ILRTDepositPool(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
    uint256 totalAssets = lrtDepositPool.getTotalAssetDeposits(asset);
    availableAssetAmount = totalAssets > assetsCommitted[asset] ? totalAssets - assetsCommitted[asset] : 0;
}
``` [2](#0-1) 

`assetsCommitted[asset]` is a global counter that increases with every successful `initiateWithdrawal` call and only decreases when the operator calls `unlockQueue`. Because `assetsCommitted` is shared across all users and is writable by any rsETH holder, an attacker can inflate it at will.

**Attack path:**

1. Protocol state: `totalAssets = 1000 ETH`, `assetsCommitted = 900 ETH`, `getAvailableAssetAmount = 100 ETH`.
2. Victim submits `initiateWithdrawal` for rsETH worth 100 ETH.
3. Attacker observes the pending transaction in the mempool and front-runs with their own `initiateWithdrawal` for rsETH worth 1 ETH.
4. Attacker's transaction executes first: `assetsCommitted` becomes 901 ETH, `getAvailableAssetAmount` drops to 99 ETH.
5. Victim's transaction executes: `100 > 99` → `revert ExceedAmountToWithdraw`.

The attacker's rsETH is locked in the withdrawal queue but can be recovered after the withdrawal delay (default 8 days). There is no fee for initiating or completing withdrawals. [3](#0-2) 

The attack is most efficient when `assetsCommitted` is already close to `totalAssets` (high "withdrawal utilization"), requiring only a tiny front-run amount to block large victim withdrawals. The attacker can sustain the DoS indefinitely by cycling rsETH: complete withdrawal → receive assets → re-deposit → re-initiate withdrawal → repeat.

`unlockQueue` is the only mechanism that reduces `assetsCommitted`, and it is restricted to `onlyAssetTransferOrOperatorRole`: [4](#0-3) 

### Impact Explanation

Users are temporarily frozen out of the withdrawal initiation path. Since `initiateWithdrawal` is the mandatory first step to recover underlying assets, blocking it prevents users from starting the withdrawal clock. With a sustained attack (attacker cycling rsETH), users may be unable to initiate withdrawals for extended periods, constituting a **temporary freezing of funds** (Medium severity).

### Likelihood Explanation

The attack requires the attacker to hold rsETH and accept an 8-day lock-up with no direct financial gain. However:
- There is no fee for initiating or completing withdrawals, so the only cost is opportunity cost.
- The attack is most effective when `assetsCommitted` is already near `totalAssets`, a realistic state during high withdrawal demand.
- The attacker can recycle their rsETH to sustain the DoS indefinitely.
- Ethereum's public mempool makes front-running straightforward.

Likelihood is **medium**.

### Recommendation

Decouple the availability check from the global `assetsCommitted` counter, or snapshot `assetsCommitted` at the time of the check and use a per-user committed amount. Alternatively, consider removing the `ExceedAmountToWithdraw` check from `initiateWithdrawal` and instead enforce it at `unlockQueue` time (when the operator actually allocates assets), similar to the recommendation in the referenced report to move the liquidity check out of the seizure path.

### Proof of Concept

```solidity
// Scenario: totalAssets = 1000e18, assetsCommitted = 900e18
// getAvailableAssetAmount = 100e18

// Victim wants to withdraw rsETH worth 100e18 assets
// Attacker front-runs with rsETH worth 1e18 assets

// Step 1: Attacker calls initiateWithdrawal (1e18 asset worth of rsETH)
// assetsCommitted becomes 901e18
// getAvailableAssetAmount becomes 99e18

// Step 2: Victim calls initiateWithdrawal (100e18 asset worth of rsETH)
// expectedAssetAmount = 100e18
// getAvailableAssetAmount = 99e18
// 100e18 > 99e18 → revert ExceedAmountToWithdraw

// Attacker waits 8 days, calls completeWithdrawal, recovers assets, repeats.
```

### Citations

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

**File:** contracts/LRTWithdrawalManager.sol (L268-281)
```text
    function unlockQueue(
        address asset,
        uint256 firstExcludedIndex,
        uint256 minimumAssetPrice,
        uint256 minimumRsEthPrice,
        uint256 maximumAssetPrice,
        uint256 maximumRsEthPrice
    )
        external
        nonReentrant
        onlySupportedAsset(asset)
        whenNotPaused
        onlyAssetTransferOrOperatorRole
        returns (uint256 rsETHBurned, uint256 assetAmountUnlocked)
```

**File:** contracts/LRTWithdrawalManager.sol (L599-603)
```text
    function getAvailableAssetAmount(address asset) public view override returns (uint256 availableAssetAmount) {
        ILRTDepositPool lrtDepositPool = ILRTDepositPool(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        uint256 totalAssets = lrtDepositPool.getTotalAssetDeposits(asset);
        availableAssetAmount = totalAssets > assetsCommitted[asset] ? totalAssets - assetsCommitted[asset] : 0;
    }
```
