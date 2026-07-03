### Title
Unbounded Gas in `updateRSETHPrice()` Due to Uncapped `supportedAssetList` Loop - (File: contracts/LRTOracle.sol)

### Summary
`LRTOracle.updateRSETHPrice()` is a public function that internally calls `_getTotalEthInProtocol()`, which iterates over the entire `supportedAssetList` with no cap. Each iteration makes expensive external calls that themselves loop over `nodeDelegatorQueue`. As the protocol adds more supported assets through normal governance, the gas cost grows unboundedly and can eventually exceed the block gas limit, permanently preventing price updates and freezing protocol fee minting.

### Finding Description

`LRTOracle._getTotalEthInProtocol()` iterates over every entry in `supportedAssets` (fetched from `lrtConfig.getSupportedAssetList()`): [1](#0-0) 

For each asset in the loop, two expensive external calls are made:

1. `getAssetPrice(asset)` — calls an external price oracle.
2. `ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset)` — which calls `getAssetDistributionData()`, which itself loops over the entire `nodeDelegatorQueue` and makes three external calls per NDC (`balanceOf`, `getAssetBalance`, `getAssetUnstaking`): [2](#0-1) 

The effective gas cost is **O(supportedAssets × nodeDelegators × external_calls_per_NDC)**. There is no cap on `supportedAssetList` in `LRTConfig`: [3](#0-2) 

`updateRSETHPrice()` is `public` and callable by any address: [4](#0-3) 

### Impact Explanation

Once the gas cost of `updateRSETHPrice()` exceeds the block gas limit, the function becomes permanently uncallable. This causes:

- **Protocol fee minting is permanently frozen**: `_updateRsETHPrice()` is the only path through which `rsethAmountToMintAsProtocolFee` is minted to the treasury. [5](#0-4) 
- **rsETH price is permanently stale**: The `rsETHPrice` storage variable can no longer be updated, causing all downstream price-dependent logic (withdrawal payout calculations, deposit minting ratios) to use an increasingly incorrect price.
- **Downside protection is disabled**: The automatic pause triggered by a price drop below threshold can no longer fire. [6](#0-5) 

Impact classification: **Medium — Unbounded gas consumption leading to permanent freezing of unclaimed yield (protocol fees) and stale price for all users.**

### Likelihood Explanation

The `addNewSupportedAsset` function is gated by `TIME_LOCK_ROLE` and represents normal, expected protocol growth — adding new LST assets over time is a core design intent. No malicious actor is required; the protocol's own governance naturally grows `supportedAssetList`. With `nodeDelegatorQueue` up to `maxNodeDelegatorLimit` (default 10) and each NDC making 3 external calls per asset, even a modest number of supported assets (e.g., 20–30) combined with 10 NDCs produces hundreds of external SLOAD/CALL operations per `updateRSETHPrice()` invocation. There is no guard or cap preventing this growth.

### Recommendation

1. **Cap `supportedAssetList`**: Add a `MAX_SUPPORTED_ASSET_COUNT` constant in `LRTConfig._addNewSupportedAsset()` and revert if exceeded, analogous to Moloch's `MAX_TOKEN_WHITELIST_COUNT`.
2. **Cache NDC balances off-chain / use a pull model**: Decouple the price update from iterating all NDCs on-chain; store per-asset TVL as a cached value updated incrementally on deposit/withdrawal events.
3. **Paginate `_getTotalEthInProtocol()`**: Allow partial updates over a subset of assets per transaction.

### Proof of Concept

1. Governance adds 30 supported LST assets via `addNewSupportedAsset` (normal operation over time).
2. `maxNodeDelegatorLimit` is set to 10 (default), with 10 active NDCs.
3. Any caller invokes `updateRSETHPrice()`.
4. `_getTotalEthInProtocol()` executes 30 outer iterations; each calls `getTotalAssetDeposits()` → `getAssetDistributionData()` → 10 NDC iterations × 3 external calls = 300 external calls total, plus 30 oracle price calls = 330 external calls.
5. At ~2,100 gas per cold SLOAD and ~700 gas per warm CALL overhead (plus EigenLayer strategy reads), the transaction exceeds the 30M block gas limit.
6. `rsETHPrice` is permanently frozen; protocol fee minting via `IRSETH.mint(treasury, ...)` can never execute again. [7](#0-6) [8](#0-7) [9](#0-8)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L270-281)
```text
        if (newRsETHPrice < highestRsethPrice) {
            uint256 diff = highestRsethPrice - newRsETHPrice;
            // normalizing to 1e18
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

            // if price decrease is off limit, pause the protocol (unless it's already paused)
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
```

**File:** contracts/LRTOracle.sol (L299-308)
```text
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
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
