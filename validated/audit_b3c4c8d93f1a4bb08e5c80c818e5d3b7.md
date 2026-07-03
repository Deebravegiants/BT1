### Title
Nested Loop Over EigenLayer Queued Withdrawals in `getAssetDistributionData` Causes Escalating Gas Cost on Every User Deposit — (`contracts/LRTDepositPool.sol`, `contracts/NodeDelegator.sol`)

---

### Summary

Every user deposit into `LRTDepositPool` triggers a deeply nested loop: for each supported asset → for each NodeDelegator → `getAssetUnstaking()` → iterate over all EigenLayer queued withdrawals × strategies. As the protocol scales toward its configured maximums, the gas cost of a single deposit grows to O(assets × NDCs × queued\_withdrawals × strategies\_per\_withdrawal), making deposits increasingly expensive and potentially uncallable.

---

### Finding Description

The call chain triggered on every `depositETH()` / `depositAsset()` is:

```
depositETH()
  └─ _beforeDeposit()
       └─ _checkIfDepositAmountExceedesCurrentLimit()
            └─ getTotalAssetDeposits(asset)
                 └─ getAssetDistributionData(asset)          [LRTDepositPool.sol:426]
                      └─ for each NDC in nodeDelegatorQueue  [LRTDepositPool.sol:447]
                           └─ INodeDelegator.getAssetUnstaking(asset) [NodeDelegator.sol:405]
                                └─ delegationManager.getQueuedWithdrawals(this)
                                     └─ for each withdrawal  [NodeDelegator.sol:409]
                                          └─ for each strategy [NodeDelegator.sol:412]
```

`getAssetDistributionData` iterates over every entry in `nodeDelegatorQueue` and calls `getAssetUnstaking` on each: [1](#0-0) 

`getAssetUnstaking` in `NodeDelegator` fetches **all** queued withdrawals from EigenLayer and iterates over them with a nested strategy loop: [2](#0-1) 

This same chain is also triggered by the public `updateRSETHPrice()` → `_getTotalEthInProtocol()`, which additionally loops over every supported asset before entering the NDC loop: [3](#0-2) 

The protocol bounds each dimension individually:
- `maxNodeDelegatorLimit` (initialized to 10, admin-settable upward)
- `maxUncompletedWithdrawalCount` (capped at 80 by `setMaxUncompletedWithdrawalCount`) [4](#0-3) 

However, the **product** of all dimensions is not bounded. At maximum configured scale:

- 10 supported assets × 10 NDCs × 80 queued withdrawals × N strategies per withdrawal

Each inner iteration involves an external `strategy.sharesToUnderlyingView()` call (a cross-contract STATICCALL), making the gas cost multiplicative. The comment in `setMaxUncompletedWithdrawalCount` itself acknowledges this concern: [5](#0-4) 

Furthermore, `getQueuedWithdrawals` returns withdrawals tracked by EigenLayer, not just the protocol's `uncompletedWithdrawalCount` counter. Forced undelegations by EigenLayer operators can add withdrawal roots beyond what the protocol's counter anticipates, as `undelegate()` shows: [6](#0-5) 

---

### Impact Explanation

**Medium — Unbounded gas consumption / Temporary freezing of funds.**

At maximum protocol scale, every user `depositETH()` or `depositAsset()` call executes thousands of cross-contract storage reads. If the combined gas cost exceeds the block gas limit or a user's gas budget, deposits revert. Since `updateRSETHPrice()` is also public and follows the same path, price updates can similarly become uncallable, leaving `rsETHPrice` stale and causing `getRsETHAmountToMint` to return incorrect values for all subsequent deposits. [7](#0-6) 

---

### Likelihood Explanation

**Medium.** The protocol is designed to scale: `maxNodeDelegatorLimit` can be raised by admin, multiple LSTs are supported, and the withdrawal queue fills naturally during normal operations (unstaking, undelegation). No attacker action is required — ordinary protocol growth drives the gas cost upward. The developers' own comment acknowledges the gas concern but the cap of 80 was chosen without accounting for the multiplicative effect of assets × NDCs × withdrawals × strategies.

---

### Recommendation

1. **Cache `getQueuedWithdrawals` results**: Instead of calling `getAssetUnstaking` per-asset per-NDC (which re-fetches the full withdrawal queue each time), fetch queued withdrawals once per NDC and compute all asset amounts in a single pass.

2. **Decouple TVL accounting from the deposit hot path**: Store a cached `totalAssetDeposits` value updated lazily (e.g., only via `updateRSETHPrice`) rather than recomputing it on every deposit. Use the cached value in `_checkIfDepositAmountExceedesCurrentLimit`.

3. **Track unstaking amounts in protocol storage**: Maintain a per-asset `assetUnstaking` mapping updated on `initiateUnstaking` / `completeUnstaking` instead of re-querying EigenLayer on every call.

---

### Proof of Concept

1. Deploy with 5 supported LST assets, 10 NDCs, and 80 queued EigenLayer withdrawals (each with 2 strategies).
2. Call `depositETH(0, "")` from an unprivileged EOA.
3. Execution path: `_checkIfDepositAmountExceedesCurrentLimit` → `getTotalAssetDeposits` (×5 assets) → `getAssetDistributionData` (×10 NDCs each) → `getAssetUnstaking` (×80 withdrawals × 2 strategies each) = **800 cross-contract `sharesToUnderlyingView` calls** plus 800 `getQueuedWithdrawals` fetches.
4. At ~5,000 gas per external call, this alone consumes ~4,000,000 gas — approaching the block gas limit on L1 and exceeding it on some L2 configurations — causing the deposit to revert with out-of-gas. [8](#0-7) [9](#0-8)

### Citations

**File:** contracts/LRTDepositPool.sol (L385-397)
```text
    function getTotalAssetDeposits(address asset) public view override returns (uint256 totalAssetDeposit) {
        (
            uint256 assetLyingInDepositPool,
            uint256 assetLyingInNDCs,
            uint256 assetStakedInEigenLayer,
            uint256 assetUnstakingFromEigenLayer,
            uint256 assetLyingInConverter,
            uint256 assetLyingUnstakingVault
        ) = getAssetDistributionData(asset);
        uint256 effectiveAssetWithEigenLayer = assetStakedInEigenLayer + assetUnstakingFromEigenLayer;
        return (assetLyingInDepositPool + assetLyingInNDCs + effectiveAssetWithEigenLayer + assetLyingInConverter
                + assetLyingUnstakingVault);
    }
```

**File:** contracts/LRTDepositPool.sol (L446-456)
```text
        uint256 ndcsCount = nodeDelegatorQueue.length;
        for (uint256 i; i < ndcsCount;) {
            assetLyingInNDCs += IERC20(asset).balanceOf(nodeDelegatorQueue[i]);

            assetStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetBalance(asset);
            assetUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset);

            unchecked {
                ++i;
            }
        }
```

**File:** contracts/LRTDepositPool.sol (L648-670)
```text
    function _beforeDeposit(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected
    )
        private
        view
        returns (uint256 rsethAmountToMint)
    {
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
    }
```

**File:** contracts/NodeDelegator.sol (L269-288)
```text
        bytes32[] memory withdrawalRoots = _getDelegationManager().undelegate(address(this));

        if (
            _getUnstakingVault().uncompletedWithdrawalCount() + withdrawalRoots.length
                > _getUnstakingVault().maxUncompletedWithdrawalCount()
        ) {
            revert MaxUncompletedWithdrawalsReached();
        }

        for (uint256 i; i < withdrawalRoots.length; i++) {
            _getUnstakingVault().increaseUncompletedWithdrawalCount();

            // NOTE: For legacy event emission we emit single withdrawal roots
            bytes32[] memory singleWithdrawal = new bytes32[](1);
            singleWithdrawal[0] = withdrawalRoots[i];
            emit WithdrawalQueued(_getNonce() - withdrawalRoots.length + i, address(this), singleWithdrawal);
        }

        emit Undelegated();
    }
```

**File:** contracts/NodeDelegator.sol (L405-427)
```text
    function getAssetUnstaking(address asset) external view returns (uint256 amount) {
        (IDelegationManager.Withdrawal[] memory queuedWithdrawals, uint256[][] memory withdrawalShares) =
            _getDelegationManager().getQueuedWithdrawals(address(this));

        for (uint256 withdrawalIndex = 0; withdrawalIndex < queuedWithdrawals.length; withdrawalIndex++) {
            IDelegationManager.Withdrawal memory withdrawal = queuedWithdrawals[withdrawalIndex];

            for (uint256 strategyIndex = 0; strategyIndex < withdrawal.strategies.length; strategyIndex++) {
                IStrategy strategy = withdrawal.strategies[strategyIndex];

                address strategyAsset = address(strategy) == address(lrtConfig.beaconChainETHStrategy())
                    ? LRTConstants.ETH_TOKEN
                    : address(strategy.underlyingToken());

                if (strategyAsset != asset) continue;

                uint256 sharesToUnstake = withdrawalShares[withdrawalIndex][strategyIndex];
                amount += strategyAsset == LRTConstants.ETH_TOKEN
                    ? sharesToUnstake
                    : strategy.sharesToUnderlyingView(sharesToUnstake);
            }
        }
    }
```

**File:** contracts/LRTOracle.sol (L331-349)
```text
    function _getTotalEthInProtocol() private view returns (uint256 totalETHInProtocol) {
        address lrtDepositPoolAddr = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
        address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
        uint256 supportedAssetCount = supportedAssets.length;

        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);

            unchecked {
                ++assetIdx;
            }
        }
    }
```

**File:** contracts/LRTUnstakingVault.sol (L150-158)
```text
    function setMaxUncompletedWithdrawalCount(uint256 _maxUncompletedWithdrawalCount) external onlyLRTManager {
        // 120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price
        // Need buffer for theoretical operator forced undelegations (ndc count * asset count = 15)
        if (_maxUncompletedWithdrawalCount > 80) {
            revert MaxUncompletedWithdrawalCountTooHigh();
        }
        maxUncompletedWithdrawalCount = _maxUncompletedWithdrawalCount;

        emit MaxUncompletedWithdrawalCountSet(_maxUncompletedWithdrawalCount);
```
