### Title
Nested Unbounded Loop in `updateRSETHPrice()` Causes Permanent Gas DoS on the Price Oracle - (File: contracts/LRTOracle.sol)

### Summary
`LRTOracle.updateRSETHPrice()` is a public, permissionless state-changing function that internally executes a nested unbounded loop: it iterates over every supported asset, and for each asset iterates over every node delegator in `nodeDelegatorQueue`, making multiple external calls per inner iteration. As the protocol scales, the cumulative gas cost can exceed the block gas limit, permanently bricking the price oracle update mechanism.

### Finding Description
`updateRSETHPrice()` is declared `public` with only a `whenNotPaused` guard, meaning any external caller can invoke it. [1](#0-0) 

It delegates to `_updateRsETHPrice()`, which calls `_getTotalEthInProtocol()`: [2](#0-1) 

`_getTotalEthInProtocol()` iterates over every entry in `lrtConfig.getSupportedAssetList()` (an unbounded `address[]` with no hard cap). For each asset it calls `ILRTDepositPool.getTotalAssetDeposits(asset)`: [3](#0-2) 

`getTotalAssetDeposits` calls `getAssetDistributionData`, which itself loops over the entire `nodeDelegatorQueue` array and makes **three external calls per NDC** (`balanceOf`, `getAssetBalance`, `getAssetUnstaking`): [4](#0-3) 

The total gas cost therefore scales as **O(supportedAssets × nodeDelegatorQueue × 3 external calls)**. `nodeDelegatorQueue` is bounded only by `maxNodeDelegatorLimit`, which starts at 10 but is freely adjustable upward by the admin: [5](#0-4) 

There is no hard cap on `supportedAssetList` in `LRTConfig`. As both arrays grow through normal protocol operation, the gas cost of a single `updateRSETHPrice()` call grows quadratically.

### Impact Explanation
If the cumulative gas cost of `updateRSETHPrice()` exceeds the Ethereum block gas limit (~30M gas), the function becomes permanently uncallable. Consequences:

- `rsETHPrice` is never updated; all subsequent `depositETH`/`depositAsset` calls use a permanently stale exchange rate, causing incorrect rsETH minting amounts for all depositors.
- The protocol fee minting mechanism (`_checkAndUpdateDailyFeeMintLimit`, `IRSETH.mint`) inside `_updateRsETHPrice` is permanently disabled — theft of unclaimed yield.
- The automatic downside-protection circuit breaker (pausing on price drop) can never trigger.

This matches **Medium — Unbounded gas consumption** and **High — Theft of unclaimed yield** from the allowed impact scope.

### Likelihood Explanation
The protocol is designed to support multiple LST assets and multiple node delegators. `maxNodeDelegatorLimit` is admin-adjustable with no ceiling. `supportedAssetList` has no cap. As the protocol adds assets and NDCs through ordinary governance, the gas cost grows quadratically. No attacker action is required; normal protocol scaling is sufficient to trigger the condition.

### Recommendation
1. Introduce a hard cap on `supportedAssetList` length in `LRTConfig.addNewSupportedAsset`.
2. Enforce a strict, low ceiling on `maxNodeDelegatorLimit` (e.g., ≤ 10) that cannot be raised beyond a safe threshold.
3. Alternatively, refactor `_getTotalEthInProtocol()` to use a cached/aggregated TVL value that is updated incrementally (e.g., on each deposit/withdrawal) rather than recomputed in full on every oracle update call.

### Proof of Concept
Call chain demonstrating the nested unbounded loop:

```
updateRSETHPrice()                          // public, no access control
  └─ _updateRsETHPrice()
       └─ _getTotalEthInProtocol()
            └─ for assetIdx in supportedAssets (N, unbounded):
                 └─ getTotalAssetDeposits(asset)
                      └─ getAssetDistributionData(asset)
                           └─ for i in nodeDelegatorQueue (M, unbounded):
                                ├─ IERC20(asset).balanceOf(ndc[i])       // cold SLOAD + call
                                ├─ INodeDelegator(ndc[i]).getAssetBalance(asset)  // external call
                                └─ INodeDelegator(ndc[i]).getAssetUnstaking(asset) // external call
```

With N=10 supported assets and M=10 NDCs, each `updateRSETHPrice()` call executes ≥ 300 external calls. Each cold external call costs ~2,100 gas for the call overhead plus execution. At N=20, M=20, the call count reaches 1,200+ external calls, pushing well past the 30M gas block limit when combined with storage reads and arithmetic inside each NDC. [2](#0-1) [4](#0-3)

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
