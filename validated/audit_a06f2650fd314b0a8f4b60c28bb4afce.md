Audit Report

## Title
Unbounded Gas in `updateRSETHPrice()` Due to Uncapped `supportedAssetList` Loop - (File: contracts/LRTOracle.sol)

## Summary
`LRTOracle.updateRSETHPrice()` is a public function that calls `_getTotalEthInProtocol()`, which iterates over the entire `supportedAssetList` with no cap. Each iteration makes expensive external calls that themselves loop over `nodeDelegatorQueue` with three external calls per NDC. As the protocol adds supported assets through normal governance, gas cost grows as O(assets × NDCs × 3) and can eventually exceed the block gas limit, permanently preventing price updates and freezing protocol fee minting.

## Finding Description
`LRTOracle.updateRSETHPrice()` is callable by any address with only a `whenNotPaused` guard: [1](#0-0) 

It calls `_updateRsETHPrice()`, which calls `_getTotalEthInProtocol()`. This private function fetches the full `supportedAssetList` from `LRTConfig` and iterates over every entry with no cap: [2](#0-1) 

For each asset, two expensive external calls are made: `getAssetPrice(asset)` (external oracle call) and `ILRTDepositPool.getTotalAssetDeposits(asset)`. The latter calls `getAssetDistributionData()`, which itself loops over the entire `nodeDelegatorQueue` making three external calls per NDC (`balanceOf`, `getAssetBalance`, `getAssetUnstaking`): [3](#0-2) 

`_addNewSupportedAsset()` in `LRTConfig` has no cap on the number of supported assets — it only checks for duplicates and zero address: [4](#0-3) 

`maxNodeDelegatorLimit` defaults to 10 at initialization: [5](#0-4) 

The effective gas cost is **O(supportedAssets × nodeDelegators × 3 external calls)**. There is no guard, pagination, or cap preventing this from growing to exceed the block gas limit.

## Impact Explanation
Once `updateRSETHPrice()` exceeds the block gas limit, it becomes permanently uncallable. This causes two concrete allowed impacts:

1. **Medium — Unbounded gas consumption**: The public `updateRSETHPrice()` function becomes permanently uncallable due to unbounded nested external call loops.
2. **Medium — Permanent freezing of unclaimed yield**: Protocol fee minting (`rsethAmountToMintAsProtocolFee` minted to treasury) occurs exclusively inside `_updateRsETHPrice()`. If this function cannot execute, all accrued protocol fees are permanently frozen: [6](#0-5) 

Additionally, `rsETHPrice` becomes permanently stale, and the downside-protection auto-pause can no longer fire: [7](#0-6) 

## Likelihood Explanation
No malicious actor is required. `addNewSupportedAsset` is gated by `TIME_LOCK_ROLE` and represents normal, expected protocol growth — adding new LST assets over time is a core design intent. With `maxNodeDelegatorLimit` defaulting to 10 and each NDC making 3 external calls per asset, even a modest number of supported assets (e.g., 20–30) combined with 10 active NDCs produces 300+ cold external CALL/SLOAD operations per `updateRSETHPrice()` invocation. The trigger itself requires no privilege — any address can call the public `updateRSETHPrice()` once the gas threshold is crossed.

## Recommendation
1. **Cap `supportedAssetList`**: Add a `MAX_SUPPORTED_ASSET_COUNT` constant in `LRTConfig._addNewSupportedAsset()` and revert if exceeded.
2. **Cache per-asset TVL**: Decouple price updates from iterating all NDCs on-chain; store per-asset TVL as a cached value updated incrementally on deposit/withdrawal events, replacing the full on-chain traversal in `_getTotalEthInProtocol()`.
3. **Paginate `_getTotalEthInProtocol()`**: Allow partial updates over a subset of assets per transaction, accumulating the total across multiple calls.

## Proof of Concept
1. Governance adds 30 supported LST assets via `addNewSupportedAsset` (normal operation over time).
2. `maxNodeDelegatorLimit` is 10 (default), with 10 active NDCs registered.
3. Any unprivileged caller invokes `updateRSETHPrice()`.
4. `_getTotalEthInProtocol()` executes 30 outer iterations; each calls `getTotalAssetDeposits()` → `getAssetDistributionData()` → 10 NDC iterations × 3 external calls = 300 external calls, plus 30 oracle price calls = 330 external calls total.
5. At ~2,100 gas per cold SLOAD and significant CALL overhead per EigenLayer strategy read, the transaction exceeds the 30M block gas limit.
6. `rsETHPrice` is permanently frozen; `IRSETH.mint(treasury, rsethAmountToMintAsProtocolFee)` can never execute again, permanently freezing all protocol fee yield.

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

**File:** contracts/LRTDepositPool.sol (L49-49)
```text
        maxNodeDelegatorLimit = 10;
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
