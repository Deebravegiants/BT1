### Title
Unbounded Nested Loop in `getAssetUnstaking()` Scales Gas Cost of All User-Facing Deposit and Price-Update Paths - (File: contracts/NodeDelegator.sol)

### Summary
`NodeDelegator.getAssetUnstaking()` contains a nested loop over all EigenLayer-queued withdrawals and their strategies. This function is called for every NodeDelegator in the queue inside `LRTDepositPool.getAssetDistributionData()` and `getETHDistributionData()`, which are themselves called for every supported asset inside `LRTOracle._getTotalEthInProtocol()`. The resulting gas cost is the product of (supported assets) × (NDC count) × (queued withdrawals per NDC) × (strategies per withdrawal). As the protocol scales through legitimate operator activity, the public functions `depositETH()`, `depositAsset()`, and `updateRSETHPrice()` can become too expensive to execute within a block gas limit, temporarily freezing deposits and price updates.

### Finding Description

`NodeDelegator.getAssetUnstaking()` fetches the full list of queued withdrawals from EigenLayer's `DelegationManager` and iterates over every withdrawal and every strategy within each withdrawal: [1](#0-0) 

This function is called inside `LRTDepositPool.getAssetDistributionData()` once per NDC in `nodeDelegatorQueue`: [2](#0-1) 

And again inside `getETHDistributionData()` once per NDC: [3](#0-2) 

`LRTOracle._getTotalEthInProtocol()` calls `ILRTDepositPool.getTotalAssetDeposits(asset)` — which calls `getAssetDistributionData()` — for **every supported asset** in a loop: [4](#0-3) 

`getTotalAssetDeposits()` is the aggregator that calls `getAssetDistributionData()`: [5](#0-4) 

The public entry points that trigger this entire chain are:

- `LRTOracle.updateRSETHPrice()` — callable by anyone with no access control: [6](#0-5) 

- `LRTDepositPool.depositETH()` and `depositAsset()` — callable by any depositor: [7](#0-6) [8](#0-7) 

Both deposit functions call `_beforeDeposit()` → `_checkIfDepositAmountExceedesCurrentLimit()` → `getTotalAssetDeposits()`, completing the chain. [9](#0-8) 

The `maxNodeDelegatorLimit` is initialized to 10 but is admin-updatable with no upper bound: [10](#0-9) [11](#0-10) 

The number of queued withdrawals per NDC is bounded by `maxUncompletedWithdrawalCount` in the unstaking vault, but this value is also admin-controlled and not enforced at the gas-cost level. As the protocol grows and operators legitimately queue many withdrawals across many NDCs, the multiplicative gas cost can exceed the block gas limit.

### Impact Explanation

When the product of (supported assets) × (NDC count) × (queued withdrawals per NDC) × (strategies per withdrawal) grows large enough, every call to `depositETH()`, `depositAsset()`, and `updateRSETHPrice()` will revert with out-of-gas. This temporarily freezes all new deposits and prevents the rsETH price from being updated, which in turn blocks the withdrawal unlock flow (`unlockQueue` depends on `rsETHPrice` being current). This constitutes a **temporary freezing of funds** for all depositors and withdrawal requestors.

### Likelihood Explanation

The protocol is designed to scale: more supported assets are added via governance, more NDCs are added to distribute EigenLayer delegation, and operators routinely queue withdrawals as part of normal restaking operations. All three multipliers grow through legitimate protocol usage. No adversarial action is required — the condition arises organically as the protocol matures. The likelihood is medium because it requires the protocol to reach a certain scale, but there is no mechanism preventing it.

### Recommendation

1. Cache the result of `getAssetUnstaking()` per NDC per block, or restructure `getAssetDistributionData()` to call `getAssetUnstaking()` once per NDC across all assets rather than once per (NDC × asset) pair.
2. Enforce an explicit cap on `maxNodeDelegatorLimit` and `maxUncompletedWithdrawalCount` that is validated against the block gas limit at configuration time.
3. Consider separating the accounting of unstaking amounts into a storage variable updated lazily (on `initiateUnstaking` / `completeUnstaking`) rather than recomputing it by iterating EigenLayer's queue on every read.

### Proof of Concept

1. Admin adds 5 supported assets to `LRTConfig`.
2. Admin adds 10 NDCs to `LRTDepositPool` (`maxNodeDelegatorLimit = 10`).
3. Operator calls `initiateUnstaking()` on each NDC until each NDC has `maxUncompletedWithdrawalCount` queued withdrawals, each with multiple strategies.
4. Any user calls `depositETH(1 ether, "")`.
5. The call chain `depositETH → _beforeDeposit → getTotalAssetDeposits → getAssetDistributionData → getAssetUnstaking` executes the nested loop 5 × 10 × W × K times (W = withdrawals per NDC, K = strategies per withdrawal).
6. At sufficient scale, the transaction reverts with out-of-gas, and no new deposits can be made.
7. Similarly, `updateRSETHPrice()` called by any address triggers `_getTotalEthInProtocol()` with the same loop structure, preventing price updates and blocking the withdrawal unlock queue.

### Citations

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

**File:** contracts/LRTDepositPool.sol (L49-49)
```text
        maxNodeDelegatorLimit = 10;
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

**File:** contracts/LRTDepositPool.sol (L99-118)
```text
    function depositAsset(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedERC20Token(asset)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);

        emit AssetDeposit(msg.sender, asset, depositAmount, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L290-297)
```text
    function updateMaxNodeDelegatorLimit(uint256 maxNodeDelegatorLimit_) external onlyLRTAdmin {
        if (maxNodeDelegatorLimit_ < nodeDelegatorQueue.length) {
            revert InvalidMaximumNodeDelegatorLimit();
        }

        maxNodeDelegatorLimit = maxNodeDelegatorLimit_;
        emit MaxNodeDelegatorLimitUpdated(maxNodeDelegatorLimit);
    }
```

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

**File:** contracts/LRTDepositPool.sol (L482-493)
```text
        uint256 ndcsCount = nodeDelegatorQueue.length;

        for (uint256 i; i < ndcsCount;) {
            ethLyingInNDCs += nodeDelegatorQueue[i].balance;

            ethStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();
            ethUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i])
                .getAssetUnstaking(LRTConstants.ETH_TOKEN);
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

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L336-348)
```text
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
```
