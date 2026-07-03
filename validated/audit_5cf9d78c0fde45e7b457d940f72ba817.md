### Title
Unbounded Nested Gas Loops in `updateRSETHPrice()` Can Permanently Brick the Price Oracle - (File: contracts/LRTOracle.sol)

### Summary
`LRTOracle.updateRSETHPrice()` is a public, permissionless function that contains nested unbounded loops over `supportedAssets`, `nodeDelegatorQueue`, and EigenLayer queued withdrawals. As the protocol scales, the gas cost grows as O(assets × NDCs × queued_withdrawals_per_NDC) with no hard cap on any dimension. If the cumulative gas exceeds the block gas limit, the function becomes permanently uncallable, freezing the rsETH price oracle and breaking all protocol operations that depend on it.

### Finding Description

`LRTOracle.updateRSETHPrice()` is callable by any external account with no access control. It internally calls `_updateRsETHPrice()` → `_getTotalEthInProtocol()`, which iterates over every entry in `supportedAssetList`: [1](#0-0) 

For each supported asset, it calls `ILRTDepositPool.getTotalAssetDeposits(asset)` → `getAssetDistributionData(asset)`, which iterates over every entry in `nodeDelegatorQueue`: [2](#0-1) 

For each NDC, it calls `INodeDelegator.getAssetUnstaking(asset)`, which fetches and iterates over all EigenLayer queued withdrawals for that NDC: [3](#0-2) 

**No hard cap exists on `supportedAssetList.length`** — `_addNewSupportedAsset()` pushes unconditionally with no length check: [4](#0-3) 

**No hard cap exists on `maxNodeDelegatorLimit`** — the admin setter accepts any value ≥ current queue length: [5](#0-4) 

The same nested loop is also triggered on every user deposit via `depositETH()` / `depositAsset()` → `_beforeDeposit()` → `_checkIfDepositAmountExceedesCurrentLimit()` → `getTotalAssetDeposits()`: [6](#0-5) 

### Impact Explanation

If `updateRSETHPrice()` reverts out-of-gas, `rsETHPrice` can no longer be updated. All downstream consumers of `rsETHPrice` are affected:

- `LRTWithdrawalManager.getExpectedAssetAmount()` and `unlockQueue()` use `lrtOracle.rsETHPrice()` — withdrawal processing halts.
- `LRTDepositPool.getRsETHAmountToMint()` uses `lrtOracle.rsETHPrice()` — deposit minting uses a permanently stale rate. [7](#0-6) 

If `getAssetDistributionData()` itself becomes too expensive, `depositETH()` and `depositAsset()` also revert, causing **temporary freezing of funds** (Medium impact).

### Likelihood Explanation

The protocol is designed to support multiple LSTs and multiple NodeDelegators. `supportedAssetList` already contains ETH, stETH, ETHx, and potentially more. Each NDC can have up to `maxUncompletedWithdrawalCount` queued EigenLayer withdrawals. As the protocol scales to support more assets and more NDCs (which is the stated design intent), the gas cost of `updateRSETHPrice()` grows multiplicatively. This is a realistic operational scenario, not a theoretical edge case.

### Recommendation

1. Introduce an explicit hard cap on `supportedAssetList.length` in `_addNewSupportedAsset()`.
2. Introduce an explicit hard cap on `maxNodeDelegatorLimit` in `updateMaxNodeDelegatorLimit()`.
3. Consider caching per-asset totals and updating them incrementally rather than recomputing the full sum on every call.
4. Alternatively, split `_getTotalEthInProtocol()` into a paginated or off-chain-assisted pattern so that no single transaction must iterate the full state.

### Proof of Concept

Call chain for any external caller:

```
updateRSETHPrice()                          // public, no access control
  └─ _updateRsETHPrice()
       └─ _getTotalEthInProtocol()
            └─ for each asset in supportedAssetList:          // loop 1 — no cap
                 └─ getTotalAssetDeposits(asset)
                      └─ getAssetDistributionData(asset)
                           └─ for each NDC in nodeDelegatorQueue:  // loop 2 — no cap
                                └─ getAssetUnstaking(asset)
                                     └─ for each queued withdrawal: // loop 3 — bounded by maxUncompletedWithdrawalCount
```

With N assets, M NDCs, and K queued withdrawals per NDC, total iterations = N × M × K. At current EVM gas costs (~2100 gas per cold SLOAD), even modest values (e.g., 10 assets × 20 NDCs × 50 withdrawals = 10,000 iterations) can approach or exceed the 30M block gas limit when accounting for external calls and memory allocation. [8](#0-7) [9](#0-8) [10](#0-9) [11](#0-10)

### Citations

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

**File:** contracts/LRTConfig.sol (L106-118)
```text
    function _addNewSupportedAsset(address asset, uint256 depositLimit) private {
        UtilLib.checkNonZeroAddress(asset);
        if (depositLimit == 0) {
            revert InvalidDepositLimit();
        }
        if (isSupportedAsset[asset]) {
            revert AssetAlreadySupported();
        }
        isSupportedAsset[asset] = true;
        supportedAssetList.push(asset);
        depositLimitByAsset[asset] = depositLimit;
        emit AddedNewSupportedAsset(asset, depositLimit);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L590-594)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```
