### Title
Unsupported ERC20 Reward Tokens Permanently Frozen in FeeReceiver — (`contracts/FeeReceiver.sol`)

---

### Summary

`NodeDelegator.processClaim()` forwards all EigenLayer reward tokens directly to the `eigenLayerRewardReceiver` address (the `FeeReceiver` contract). `FeeReceiver` only handles ETH and has no ERC20 recovery mechanism. Any reward token that is not a supported asset in `LRTConfig` becomes permanently frozen in `FeeReceiver` with no on-chain path to retrieve it.

---

### Finding Description

**Step 1 — Claim flow sends tokens to FeeReceiver**

`NodeDelegator.processClaim()` calls EigenLayer's `RewardsCoordinator.processClaim()` with `lrtConfig.eigenLayerRewardReceiver()` as the recipient: [1](#0-0) 

EigenLayer's `RewardsCoordinator` then ERC20-transfers the claimed reward tokens (EIGEN, wETH, AVS-specific tokens, etc.) directly to that address.

**Step 2 — FeeReceiver only handles ETH**

`FeeReceiver.sendFunds()` is the sole outbound function and it only forwards the contract's native ETH balance: [2](#0-1) 

There is no `recoverTokens()`, no ERC20 `transfer`, and no other function that touches ERC20 balances. `FeeReceiver` does not inherit `Recoverable`: [3](#0-2) 

Compare with `Recoverable`, which does provide `recoverTokens()` but is a separate abstract contract not used by `FeeReceiver`: [4](#0-3) 

**Step 3 — NodeDelegator's transfer path is irrelevant and also blocked**

`NodeDelegator.transferBackToLRTDepositPool()` is gated by `onlySupportedAsset`: [5](#0-4) 

Even if this were relevant, the reward tokens land in `FeeReceiver`, not in `NodeDelegator`, so this function cannot help.

---

### Impact Explanation

Any ERC20 reward token distributed by EigenLayer that is not registered in `LRTConfig.supportedAssetList` (e.g., the EIGEN token, wETH if not supported, or any AVS-specific token) is permanently frozen in `FeeReceiver`. The tokens cannot be forwarded to the deposit pool, cannot be counted in rsETH TVL, and cannot be recovered by any on-chain call. This matches the allowed impact: **Medium — Permanent freezing of unclaimed yield**.

---

### Likelihood Explanation

EigenLayer's `RewardsCoordinator` is designed to distribute arbitrary ERC20 tokens (AVS operators choose the reward token). The EIGEN token itself is a primary reward token. It is realistic — and already occurring on mainnet — that reward distributions include tokens not in the protocol's supported asset list. The operator-callable `processClaim` is a normal operational path, not an attack vector requiring any adversarial action.

---

### Recommendation

Add an ERC20 recovery function to `FeeReceiver`, or have it inherit `Recoverable`. A minimal fix:

```solidity
function recoverERC20(address token, address recipient, uint256 amount)
    external
    onlyRole(DEFAULT_ADMIN_ROLE)
{
    IERC20(token).safeTransfer(recipient, amount);
}
```

Alternatively, route ERC20 rewards through a dedicated handler that can swap or forward them into the deposit pool.

---

### Proof of Concept

```solidity
// Fork test (Foundry, mainnet fork)
function test_rewardTokenFrozenInFeeReceiver() external {
    // 1. Operator calls processClaim with a valid EIGEN reward claim
    vm.prank(operator);
    nodeDelegator.processClaim(eigenRewardClaim);

    // 2. EIGEN tokens land in FeeReceiver (eigenLayerRewardReceiver)
    address feeReceiver = lrtConfig.eigenLayerRewardReceiver();
    uint256 frozen = IERC20(EIGEN_TOKEN).balanceOf(feeReceiver);
    assertGt(frozen, 0);

    // 3. sendFunds() only moves ETH — EIGEN balance unchanged
    FeeReceiver(payable(feeReceiver)).sendFunds();
    assertEq(IERC20(EIGEN_TOKEN).balanceOf(feeReceiver), frozen);

    // 4. No other on-chain function can move the tokens out
    // transferBackToLRTDepositPool reverts: EIGEN not a supported asset
    vm.prank(assetTransferRole);
    vm.expectRevert(ILRTConfig.AssetNotSupported.selector);
    nodeDelegator.transferBackToLRTDepositPool(EIGEN_TOKEN, frozen);
}
```

### Citations

**File:** contracts/NodeDelegator.sol (L202-209)
```text
    function processClaim(IRewardsCoordinator.RewardsMerkleClaim calldata claim)
        external
        nonReentrant
        onlyLRTOperator
        whenNotPaused
    {
        IRewardsCoordinator(lrtConfig.rewardsCoordinator()).processClaim(claim, lrtConfig.eigenLayerRewardReceiver());
    }
```

**File:** contracts/NodeDelegator.sol (L467-476)
```text
    function transferBackToLRTDepositPool(
        address asset,
        uint256 amount
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedAsset(asset)
        onlyAssetTransferRole
    {
```

**File:** contracts/FeeReceiver.sol (L13-13)
```text
contract FeeReceiver is IFeeReceiver, Initializable, AccessControlUpgradeable {
```

**File:** contracts/FeeReceiver.sol (L53-58)
```text
    function sendFunds() external {
        uint256 balance = address(this).balance;
        ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();

        emit MevRewardsAddedToTVL(balance);
    }
```

**File:** contracts/utils/Recoverable.sol (L41-57)
```text
    function recoverTokens(
        address tokenAddress,
        address recipient,
        uint256 amount
    )
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        UtilLib.checkNonZeroAddress(tokenAddress);
        UtilLib.checkNonZeroAddress(recipient);
        if (amount == 0) revert ZeroAmount();
        if (IERC20(tokenAddress).balanceOf(address(this)) < amount) revert InsufficientBalance();

        IERC20(tokenAddress).safeTransfer(recipient, amount);

        emit TokensRecovered(tokenAddress, recipient, amount);
    }
```
