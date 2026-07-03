### Title
`LRTWithdrawalManager::initiateWithdrawal` Can Be DoSed via Front-Running Dust Withdrawal - (File: contracts/LRTWithdrawalManager.sol)

---

### Summary

`LRTWithdrawalManager.initiateWithdrawal` checks that the caller's expected asset amount does not exceed `getAvailableAssetAmount(asset)` and reverts with `ExceedAmountToWithdraw` if it does. Because `getAvailableAssetAmount` is derived from the mutable `assetsCommitted[asset]` mapping, any unprivileged user can front-run a victim's withdrawal by submitting a dust-sized `initiateWithdrawal` in the same block, incrementing `assetsCommitted[asset]` by a small amount and causing the victim's transaction to revert.

---

### Finding Description

`initiateWithdrawal` performs the following sequence:

1. Transfers the caller's rsETH into the contract.
2. Computes `expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked)`.
3. Checks `if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw()`.
4. Increments `assetsCommitted[asset] += expectedAssetAmount`. [1](#0-0) 

`getAvailableAssetAmount` is computed as:

```
totalAssets - assetsCommitted[asset]
``` [2](#0-1) 

Because `assetsCommitted[asset]` is a shared, incrementable state variable, an attacker who calls `initiateWithdrawal` with the protocol minimum (`minRsEthAmountToWithdraw[asset]`) in the same block as the victim will:

- Increase `assetsCommitted[asset]` by `getExpectedAssetAmount(asset, minRsEthAmountToWithdraw[asset])`.
- Reduce `getAvailableAssetAmount(asset)` by the same amount.
- Cause the victim's transaction to revert with `ExceedAmountToWithdraw` if the victim's `expectedAssetAmount` was at or near the available limit. [3](#0-2) 

The attacker's rsETH is not lost — it is locked in a withdrawal request and can be recovered by later calling `completeWithdrawal`. The only cost to the attacker is gas and the temporary opportunity cost of locked rsETH. [4](#0-3) 

---

### Impact Explanation

A victim attempting to queue a withdrawal at or near the current available asset ceiling is temporarily blocked. The attacker can repeat this front-run every time the victim retries, sustaining the DoS across multiple blocks. This constitutes **temporary freezing of funds** (the victim's rsETH is returned on revert, but their ability to initiate a withdrawal is persistently denied).

**Impact: Medium — Temporary freezing of funds.**

---

### Likelihood Explanation

- The attack requires no special privileges; any rsETH holder can call `initiateWithdrawal`.
- The attacker needs only the protocol minimum amount of rsETH (`minRsEthAmountToWithdraw[asset]`), which is a small, configurable threshold.
- The attack is most effective when available asset capacity is nearly fully committed (i.e., `getAvailableAssetAmount` ≈ victim's `expectedAssetAmount`), a realistic condition during high withdrawal demand.
- On Ethereum mainnet, MEV infrastructure makes same-block front-running straightforward.
- The attacker's rsETH is recoverable, so the sustained cost is only gas.

**Likelihood: Medium.**

---

### Recommendation

Replace the hard revert with a `min`-based approach, analogous to the fix applied in the referenced `forceReplenish` report. Accept up to the available amount rather than reverting when the requested amount slightly exceeds availability:

```solidity
uint256 available = getAvailableAssetAmount(asset);
uint256 effectiveAssetAmount = expectedAssetAmount < available ? expectedAssetAmount : available;
if (effectiveAssetAmount == 0) revert ExceedAmountToWithdraw();

// Recalculate rsETH to burn proportionally if capped
uint256 effectiveRsETH = effectiveAssetAmount == expectedAssetAmount
    ? rsETHUnstaked
    : (rsETHUnstaked * effectiveAssetAmount) / expectedAssetAmount;

assetsCommitted[asset] += effectiveAssetAmount;
_addUserWithdrawalRequest(asset, effectiveRsETH, effectiveAssetAmount);
```

Alternatively, refund excess rsETH to the caller when the requested amount is partially capped.

---

### Proof of Concept

```solidity
function testInitiateWithdrawalFrontRunDoS() public {
    // Setup: victim has rsETH and wants to withdraw the full available amount
    uint256 victimRsETH = getMaxWithdrawableRsETH(asset);
    uint256 dustRsETH = minRsEthAmountToWithdraw[asset];

    // Attacker front-runs with dust amount in the same block
    vm.startPrank(attacker);
    rsETH.approve(address(withdrawalManager), dustRsETH);
    withdrawalManager.initiateWithdrawal(asset, dustRsETH, "");
    // assetsCommitted[asset] is now increased by dust expectedAssetAmount
    vm.stopPrank();

    // Victim's transaction now reverts because available capacity was reduced
    vm.startPrank(victim);
    rsETH.approve(address(withdrawalManager), victimRsETH);
    vm.expectRevert(LRTWithdrawalManager.ExceedAmountToWithdraw.selector);
    withdrawalManager.initiateWithdrawal(asset, victimRsETH, "");
    vm.stopPrank();

    // Attacker's rsETH is not lost — they can complete withdrawal later
    // Victim is blocked and must retry, only to be front-run again
}
``` [5](#0-4) [2](#0-1)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L35-53)
```text
    mapping(address asset => uint256) public minRsEthAmountToWithdraw;
    uint256 public withdrawalDelayBlocks;

    // Next available nonce for withdrawal requests per asset, indicating total requests made.
    mapping(address asset => uint256 nonce) public nextUnusedNonce;

    // Next nonce for which a withdrawal request remains locked.
    mapping(address asset => uint256 requestNonce) public nextLockedNonce;

    // Mapping from a unique request identifier to its corresponding withdrawal request
    mapping(bytes32 requestId => WithdrawalRequest) public withdrawalRequests;

    // Maps each asset to user addresses, pointing to an ordered list of their withdrawal request nonces.
    // Utilizes a double-ended queue for efficient management and removal of initial requests.
    mapping(address asset => mapping(address user => DoubleEndedQueue.Uint256Deque requestNonces)) public
        userAssociatedNonces;

    // Asset amount committed to be withdrawn by users.
    mapping(address asset => uint256 amount) public assetsCommitted;
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

**File:** contracts/LRTWithdrawalManager.sol (L599-603)
```text
    function getAvailableAssetAmount(address asset) public view override returns (uint256 availableAssetAmount) {
        ILRTDepositPool lrtDepositPool = ILRTDepositPool(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        uint256 totalAssets = lrtDepositPool.getTotalAssetDeposits(asset);
        availableAssetAmount = totalAssets > assetsCommitted[asset] ? totalAssets - assetsCommitted[asset] : 0;
    }
```
