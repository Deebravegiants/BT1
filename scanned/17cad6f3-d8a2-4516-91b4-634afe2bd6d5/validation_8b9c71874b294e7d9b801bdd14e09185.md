### Title
Unbounded Gas Consumption in `updateRSETHPrice()` via Nested Loops Over `nodeDelegatorQueue` and `supportedAssetList` - (File: contracts/LRTOracle.sol)

### Summary
`LRTOracle.updateRSETHPrice()` is a publicly callable function that internally iterates over all supported assets and, for each asset, calls `getTotalAssetDeposits()` which itself iterates over all NodeDelegator contracts (NDCs). As both arrays grow, the gas cost of this function grows as O(assets × NDCs), with no upper bound enforced on the number of supported assets. This can cause the price update to become uncallable, permanently freezing the rsETH price and blocking deposits and withdrawals.

### Finding Description

`LRTOracle.updateRSETHPrice()` is permissionless (no role check) and calls `_updateRsETHPrice()`, which calls `_getTotalEthInProtocol()`. [1](#0-0) 

`_getTotalEthInProtocol()` iterates over every entry in `supportedAssetList`: [2](#0-1) 

For each asset, it calls `ILRTDepositPool.getTotalAssetDeposits(asset)`, which calls `getAssetDistributionData()`, which itself loops over every NDC in `nodeDelegatorQueue`, making 3 external calls per NDC per asset (`balanceOf`, `getAssetBalance`, `getAssetUnstaking`): [3](#0-2) 

The ETH path (`getETHDistributionData`) similarly loops over all NDCs: [4](#0-3) 

`supportedAssetList` has no enforced maximum size — `addNewSupportedAsset` simply pushes to the array: [5](#0-4) 

`nodeDelegatorQueue` is capped at `maxNodeDelegatorLimit` (initialized to 10), but `maxNodeDelegatorLimit` itself can be updated by the admin with no hard ceiling: [6](#0-5) 

Each external call to an NDC costs ~2,100–5,000 gas (cold SLOAD + external call overhead). With N assets and M NDCs, the loop executes N×M×3 external calls. At 10 NDCs and 10 assets that is already 300 external calls. As the protocol scales, this function will exceed the block gas limit.

### Impact Explanation

When `updateRSETHPrice()` runs out of gas, the rsETH price becomes permanently stale. Because `depositAsset` and `depositETH` call `getRsETHAmountToMint` which reads `lrtOracle.rsETHPrice()`, a stale price does not directly block deposits, but the price oracle update itself becomes permanently uncallable. More critically, the price-decrease circuit breaker in `_updateRsETHPrice()` that pauses the protocol on a large price drop also becomes unreachable, disabling a key safety mechanism. This constitutes **unbounded gas consumption** (Medium impact per scope) with a realistic path to **temporary or permanent freezing of funds** if the price update is required for withdrawal unlocking logic.

### Likelihood Explanation

The protocol is designed to support multiple LST assets and multiple NDCs. As the protocol grows (more assets added via `addNewSupportedAsset`, more NDCs added), the gas cost grows multiplicatively. This is a realistic operational scenario, not a theoretical edge case. `updateRSETHPrice()` has no access control, so any caller (including a keeper bot) will hit the gas limit once the arrays are large enough.

### Recommendation

1. Enforce a hard cap on `supportedAssetList` length in `_addNewSupportedAsset`.
2. Enforce a hard cap on `maxNodeDelegatorLimit` that cannot be raised beyond a safe bound.
3. Consider caching TVL per asset off-chain and using a push-based oracle pattern rather than computing the full TVL on-chain in a single transaction.
4. Alternatively, split `_getTotalEthInProtocol` into paginated calls so no single transaction must iterate all assets × all NDCs.

### Proof of Concept

Call path for a single `updateRSETHPrice()` invocation with A assets and N NDCs:

```
updateRSETHPrice()
  └─ _updateRsETHPrice()
       └─ _getTotalEthInProtocol()
            └─ for each asset (A iterations):
                 └─ getTotalAssetDeposits(asset)
                      └─ getAssetDistributionData(asset)
                           └─ for each NDC (N iterations):
                                ├─ IERC20(asset).balanceOf(ndc[i])       // external call
                                ├─ INodeDelegator(ndc[i]).getAssetBalance(asset)  // external call
                                └─ INodeDelegator(ndc[i]).getAssetUnstaking(asset) // external call
```

Total external calls = A × N × 3. At A=10, N=10: 300 external calls ≈ 300 × ~5,000 gas = 1,500,000 gas for calls alone, plus loop overhead, storage reads, and the ETH path loop. As A and N grow, this exceeds the 30M Ethereum mainnet block gas limit. [1](#0-0) [2](#0-1) [7](#0-6) [8](#0-7) [9](#0-8)

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

**File:** contracts/LRTDepositPool.sol (L29-33)
```text
    uint256 public maxNodeDelegatorLimit;
    uint256 public minAmountToDeposit;

    mapping(address => uint256) public isNodeDelegator; // 0: not a node delegator, 1: is a node delegator
    address[] public nodeDelegatorQueue;
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

**File:** contracts/LRTDepositPool.sol (L426-462)
```text
    function getAssetDistributionData(address asset)
        public
        view
        override
        onlySupportedAsset(asset)
        returns (
            uint256 assetLyingInDepositPool,
            uint256 assetLyingInNDCs,
            uint256 assetStakedInEigenLayer,
            uint256 assetUnstakingFromEigenLayer,
            uint256 assetLyingInConverter,
            uint256 assetLyingUnstakingVault
        )
    {
        if (asset == LRTConstants.ETH_TOKEN) {
            return getETHDistributionData();
        }

        assetLyingInDepositPool = IERC20(asset).balanceOf(address(this));

        uint256 ndcsCount = nodeDelegatorQueue.length;
        for (uint256 i; i < ndcsCount;) {
            assetLyingInNDCs += IERC20(asset).balanceOf(nodeDelegatorQueue[i]);

            assetStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetBalance(asset);
            assetUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset);

            unchecked {
                ++i;
            }
        }

        address lrtUnstakingVault = lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT);

        assetLyingInConverter = 0; // assets in converter are accounted in their eth value => getETHDistributionData()
        assetLyingUnstakingVault = IERC20(asset).balanceOf(lrtUnstakingVault);
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

**File:** contracts/LRTConfig.sol (L99-118)
```text
    function addNewSupportedAsset(address asset, uint256 depositLimit) external onlyRole(LRTConstants.TIME_LOCK_ROLE) {
        _addNewSupportedAsset(asset, depositLimit);
    }

    /// @dev private function to add a new supported asset
    /// @param asset Asset address
    /// @param depositLimit Deposit limit for the asset
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
