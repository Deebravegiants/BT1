### Title
Unbounded Loop in `_getTotalEthInProtocol()` Can Permanently Brick `updateRSETHPrice()` - (File: contracts/LRTOracle.sol)

---

### Summary

`LRTOracle._getTotalEthInProtocol()` iterates over the `supportedAssetList` array, which has no hard cap. Each iteration triggers a nested chain of external calls and inner loops over `nodeDelegatorQueue` and EigenLayer queued withdrawals. As the protocol adds more supported assets, the gas cost of `updateRSETHPrice()` (a public, permissionless function) grows without bound and can permanently exceed the block gas limit, freezing the rsETH price oracle.

---

### Finding Description

`LRTOracle._getTotalEthInProtocol()` is the private function that computes the total ETH value backing rsETH. It is called unconditionally by both `updateRSETHPrice()` (public, no access control) and `updateRSETHPriceAsManager()` (manager-only). [1](#0-0) 

The outer loop iterates over every entry in `supportedAssetList`: [2](#0-1) 

`supportedAssetList` is grown by `_addNewSupportedAsset()` with no upper bound: [3](#0-2) 

For each supported asset, the loop calls `ILRTDepositPool.getTotalAssetDeposits(asset)` → `getAssetDistributionData()`, which itself loops over every entry in `nodeDelegatorQueue` (up to `maxNodeDelegatorLimit`, default 10): [4](#0-3) 

For each NDC in that inner loop, `getAssetUnstaking()` is called, which in turn loops over all EigenLayer queued withdrawals for that NDC (bounded by `maxUncompletedWithdrawalCount`, max 80): [5](#0-4) 

The total gas complexity is therefore **O(assets × NDCs × queued\_withdrawals)**. With the current caps of 10 NDCs and 80 queued withdrawals, each supported asset costs on the order of ~180,000 gas in external calls and storage reads. At ~170 supported assets the function would exceed Ethereum's ~30M block gas limit. There is no pagination, no index parameter, and no fallback path — both `updateRSETHPrice()` and `updateRSETHPriceAsManager()` call the same unbounded `_updateRsETHPrice()` → `_getTotalEthInProtocol()` chain. [6](#0-5) 

---

### Impact Explanation

`rsETHPrice` is the single stored value read by every deposit (`getRsETHAmountToMint`) and every withdrawal (`getExpectedAssetAmount`). If `updateRSETHPrice()` becomes permanently uncallable, the stored price goes stale. Users depositing or withdrawing against a stale price receive incorrect rsETH or asset amounts — a form of share/asset mis-accounting. Additionally, the price-deviation circuit-breaker that auto-pauses the protocol on large price drops can never fire, removing a critical safety mechanism. **Impact: Medium — unbounded gas consumption leading to permanent freezing of the price oracle and incorrect protocol accounting.**

---

### Likelihood Explanation

`addNewSupportedAsset()` requires `TIME_LOCK_ROLE` and is a legitimate protocol-growth action. The protocol currently supports 2–3 assets, so the threshold is not reached today. However, there is no on-chain cap preventing the list from growing to a size that breaks the function. As the protocol expands to support additional LSTs, the risk increases monotonically. No malicious actor is required; ordinary protocol growth is sufficient.

---

### Recommendation

1. **Add a hard cap** on `supportedAssetList.length` inside `_addNewSupportedAsset()` (e.g., `require(supportedAssetList.length < MAX_ASSETS)`).
2. **Alternatively**, refactor `_getTotalEthInProtocol()` to accept `startIndex` / `endIndex` parameters so the price update can be executed in multiple transactions.
3. **Cache per-asset TVL** in a mapping updated lazily on deposit/withdrawal, so `_getTotalEthInProtocol()` reads cached values instead of re-computing via nested external calls.

---

### Proof of Concept

1. Admin (via timelock) calls `addNewSupportedAsset()` repeatedly, growing `supportedAssetList` to N entries (N ≈ 170 with current NDC/withdrawal caps).
2. Any caller invokes `updateRSETHPrice()`.
3. Execution enters `_getTotalEthInProtocol()`, which loops N times; each iteration calls `getTotalAssetDeposits()` → `getAssetDistributionData()` → 10 NDC iterations → each NDC calls `getAssetUnstaking()` → up to 80 EigenLayer withdrawal iterations.
4. Total gas ≈ 170 × 10 × 80 × ~2,000 gas/iteration ≈ 27,200,000 gas, approaching or exceeding the block gas limit.
5. The transaction reverts with out-of-gas. `rsETHPrice` is never updated. All subsequent calls to `updateRSETHPrice()` and `updateRSETHPriceAsManager()` also revert, permanently freezing the oracle.

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

**File:** contracts/NodeDelegator.sol (L406-427)
```text
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
