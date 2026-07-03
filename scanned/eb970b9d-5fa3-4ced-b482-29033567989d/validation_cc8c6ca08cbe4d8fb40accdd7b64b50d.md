### Title
Unbounded Nested Loops in `NodeDelegator.getAssetUnstaking()` Transitively Block `updateRSETHPrice()` and User Deposits - (File: contracts/NodeDelegator.sol)

---

### Summary

`NodeDelegator.getAssetUnstaking()` contains nested loops over all queued EigenLayer withdrawals and their strategies. This function is called once per NDC per asset inside `getAssetDistributionData()` / `getETHDistributionData()`, which feeds into `getTotalAssetDeposits()`, which is invoked by both the public `LRTOracle.updateRSETHPrice()` and the user-facing `LRTDepositPool.depositETH()` / `depositAsset()`. As the number of NDCs, queued withdrawals, and supported assets grows, the cumulative gas cost can exceed the block gas limit, permanently bricking price updates and user deposits.

---

### Finding Description

`NodeDelegator.getAssetUnstaking()` fetches all queued EigenLayer withdrawals for the NDC and iterates over them in a nested loop: [1](#0-0) 

For each of the `W` queued withdrawals it iterates over `S` strategies, making this O(W × S) per call.

This function is called inside `getAssetDistributionData()` once per NDC in the queue: [2](#0-1) 

And again inside `getETHDistributionData()` once per NDC: [3](#0-2) 

Both feed into `getTotalAssetDeposits()`: [4](#0-3) 

`LRTOracle._getTotalEthInProtocol()` calls `getTotalAssetDeposits()` for **every supported asset** in a loop: [5](#0-4) 

`_getTotalEthInProtocol()` is called by the public `updateRSETHPrice()`: [6](#0-5) 

On the deposit path, `_checkIfDepositAmountExceedesCurrentLimit()` calls `getTotalAssetDeposits()`: [7](#0-6) 

Which is invoked from `_beforeDeposit()` inside `depositETH()` and `depositAsset()`: [8](#0-7) 

The full call-depth nesting for `updateRSETHPrice()` is:

```
updateRSETHPrice()
  └─ _getTotalEthInProtocol()                    [loop: A supported assets]
       └─ getTotalAssetDeposits(asset)
            └─ getAssetDistributionData(asset)   [loop: N NDCs]
                 └─ getAssetUnstaking(asset)     [loop: W withdrawals × S strategies]
```

Total iterations: **A × N × W × S**, each involving external calls to EigenLayer's `DelegationManager.getQueuedWithdrawals()` and `strategy.sharesToUnderlyingView()`.

With realistic protocol parameters:
- `A` = 3–5 supported assets
- `N` = up to 10 NDCs (`maxNodeDelegatorLimit` initialized to 10)
- `W` = up to 80 queued withdrawals per NDC (`maxUncompletedWithdrawalCount` ≤ 80)
- `S` = 1–3 strategies per withdrawal

Worst case: 5 × 10 × 80 × 3 = **12,000 iterations** with external SLOAD-heavy calls, easily exceeding the block gas limit. [9](#0-8) 

---

### Impact Explanation

If `updateRSETHPrice()` reverts due to out-of-gas, the rsETH/ETH exchange rate cannot be updated. Since `depositETH()` and `depositAsset()` also traverse the same loop via `_checkIfDepositAmountExceedesCurrentLimit()`, they revert too. Users are unable to deposit assets into the protocol. This constitutes **temporary freezing of funds** (Medium severity).

---

### Likelihood Explanation

The protocol is designed to scale: `maxNodeDelegatorLimit` is 10, `maxUncompletedWithdrawalCount` is up to 80, and multiple LSTs are supported. As the protocol matures and operators queue many EigenLayer withdrawals (e.g., during undelegation or rebalancing), the gas cost of `getAssetUnstaking()` grows proportionally. No attacker action is required — normal protocol operation causes the accumulation. Any user calling `depositETH()` or `updateRSETHPrice()` triggers the path.

---

### Recommendation

1. **Cache `getQueuedWithdrawals` results**: Instead of calling `getQueuedWithdrawals()` once per `getAssetUnstaking()` call (which is invoked A × N times), aggregate all queued withdrawal data in a single pass per NDC.
2. **Separate accounting from on-chain enumeration**: Maintain an internal mapping that tracks `assetUnstaking[ndc][asset]` updated incrementally on `initiateUnstaking()` and `completeUnstaking()`, eliminating the need to enumerate EigenLayer's withdrawal queue at read time.
3. **Limit loop depth**: Enforce a tighter cap on `maxUncompletedWithdrawalCount` per NDC, or split `updateRSETHPrice()` into a two-phase commit that processes NDCs in batches.

---

### Proof of Concept

1. Protocol has 4 supported assets, 10 NDCs, each NDC has 80 queued EigenLayer withdrawals with 2 strategies each.
2. Any user calls `updateRSETHPrice()` (public, no access control when unpaused).
3. `_getTotalEthInProtocol()` loops over 4 assets → `getTotalAssetDeposits()` → `getAssetDistributionData()` loops over 10 NDCs → `getAssetUnstaking()` loops over 80 withdrawals × 2 strategies = 160 iterations per call.
4. Total: 4 × 10 × 160 = **6,400 inner iterations**, each with external calls to EigenLayer contracts.
5. Transaction reverts with out-of-gas; rsETH price is frozen and all deposits revert. [10](#0-9) [11](#0-10)

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

**File:** contracts/LRTDepositPool.sol (L86-92)
```text
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
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

**File:** contracts/LRTDepositPool.sol (L676-682)
```text
    function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
        uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
        if (asset == LRTConstants.ETH_TOKEN) {
            return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
        }
        return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
    }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
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

**File:** contracts/LRTUnstakingVault.sol (L151-156)
```text
        // 120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price
        // Need buffer for theoretical operator forced undelegations (ndc count * asset count = 15)
        if (_maxUncompletedWithdrawalCount > 80) {
            revert MaxUncompletedWithdrawalCountTooHigh();
        }
        maxUncompletedWithdrawalCount = _maxUncompletedWithdrawalCount;
```
