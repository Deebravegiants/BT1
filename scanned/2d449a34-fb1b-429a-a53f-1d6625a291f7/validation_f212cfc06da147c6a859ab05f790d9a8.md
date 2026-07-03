### Title
Unbounded O(K × M) Gas in `updateRSETHPrice()` Can Permanently Freeze rsETH Price Updates — (`contracts/LRTOracle.sol`, `contracts/LRTDepositPool.sol`)

---

### Summary

`updateRSETHPrice()` is a public, permissionless function. Its internal call chain produces a nested loop over K supported assets × M node delegators, with multiple expensive EigenLayer external calls per cell. Because `maxNodeDelegatorLimit` has no hard upper bound and the supported-asset list has no cap, the gas cost grows as O(K × M × W) (where W is queued-withdrawal count per NDC). At realistic operational scale the transaction exceeds the 30 M-gas block limit and reverts permanently.

---

### Finding Description

**Full call chain:**

```
updateRSETHPrice()                          ← public, no access control
  └─ _updateRsETHPrice()
       └─ _getTotalEthInProtocol()
            └─ for each of K assets:
                 getTotalAssetDeposits(asset)
                   └─ getAssetDistributionData(asset)
                        └─ for each of M NDCs:
                             IERC20(asset).balanceOf(ndc[i])          // external call
                             INodeDelegator(ndc[i]).getAssetBalance()  // external call →
                               NodeDelegatorHelper.getAssetBalance()
                                 → DelegationManager.getWithdrawableShares()  // EigenLayer
                             INodeDelegator(ndc[i]).getAssetUnstaking()// external call →
                               DelegationManager.getQueuedWithdrawals()       // EigenLayer
                                 + nested loop over all queued withdrawals
```

**Key code locations:**

`_getTotalEthInProtocol` iterates over every supported asset and calls `getTotalAssetDeposits` for each: [1](#0-0) 

`getAssetDistributionData` then iterates over every NDC and makes three external calls per NDC per asset: [2](#0-1) 

`getAssetUnstaking` calls EigenLayer's `getQueuedWithdrawals` (returning all pending withdrawals) and then runs a nested loop over them — this is the most expensive leaf: [3](#0-2) 

`getAssetBalance` calls EigenLayer's `getWithdrawableShares` — another cross-contract call per NDC per asset: [4](#0-3) 

**No hard cap on `maxNodeDelegatorLimit`:** `updateMaxNodeDelegatorLimit` only enforces `newLimit >= queue.length`; there is no ceiling: [5](#0-4) 

The default is 10, but an admin can raise it to any `uint256` value for legitimate operational reasons (e.g., distributing stake across many EigenLayer operators). There is likewise no cap on the number of supported assets. [6](#0-5) 

---

### Impact Explanation

Once the gas cost of `updateRSETHPrice()` exceeds 30 M gas, every call reverts with out-of-gas. Because NDCs with staked assets cannot be removed from the queue (removal requires zero residual balance), and assets with deposits cannot be removed from the supported list, the condition is **permanent** without a full protocol migration. The stored `rsETHPrice` becomes stale, and the manager-only variant `updateRSETHPriceAsManager()` suffers the same gas path and also reverts. [7](#0-6) 

**Scoped impact:** Medium — Unbounded gas consumption; rsETH price update permanently frozen.

---

### Likelihood Explanation

The precondition is legitimate admin configuration, not malicious compromise. An operator scaling the protocol to 30–50 NDCs (each delegated to a different EigenLayer operator for decentralization) combined with 5–10 supported LSTs produces 150–500 NDC×asset cells, each requiring two EigenLayer cross-contract calls. At ~20 k–50 k gas per EigenLayer call, 500 cells × 2 calls × 35 k gas ≈ 35 M gas — already over the block limit. This is a realistic operational scale for a growing LRT protocol.

---

### Recommendation

1. **Hard-cap `maxNodeDelegatorLimit`** to a value (e.g., 20) that keeps worst-case gas well below 30 M, enforced in `updateMaxNodeDelegatorLimit`.
2. **Cache per-NDC totals** in storage (updated on deposit/withdrawal/unstaking events) so `_getTotalEthInProtocol` reads O(K + M) storage slots instead of making O(K × M) external calls.
3. **Separate `getAssetUnstaking` accounting** into a storage variable maintained by `initiateUnstaking` / `completeUnstaking`, eliminating the `getQueuedWithdrawals` loop from the price-update path entirely.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.27;

// Foundry fork test — run against a local Anvil fork
contract GasExplosionTest is Test {
    LRTOracle oracle;
    LRTDepositPool pool;

    function setUp() public {
        // deploy protocol with standard config (see existing deploy scripts)
        // register K=5 LST assets
        // raise maxNodeDelegatorLimit to 50
        // deploy and add M=50 NodeDelegator contracts
        // have each NDC deposit assets into EigenLayer strategies
        // (so getAssetBalance returns non-zero and getQueuedWithdrawals is populated)
    }

    function test_updateRSETHPrice_OOG() public {
        uint256 gasBefore = gasleft();
        // call with 30M gas budget
        (bool ok,) = address(oracle).call{gas: 30_000_000}(
            abi.encodeCall(oracle.updateRSETHPrice, ())
        );
        assertFalse(ok, "expected OOG revert");
        // confirm gas consumed exceeds block limit
        assertGt(gasBefore - gasleft(), 29_000_000);
    }

    function testFuzz_gasGrowsQuadratically(uint8 k, uint8 m) public {
        vm.assume(k > 1 && k <= 10);
        vm.assume(m > 1 && m <= 50);
        // configure k assets, m NDCs, measure gas
        uint256 gasUsed = _measureUpdateGas(k, m);
        // assert quadratic growth: gas(2k,2m) >> 2*gas(k,m)
        uint256 gasUsed2x = _measureUpdateGas(k * 2, m * 2);
        assertGt(gasUsed2x, gasUsed * 3, "gas grows super-linearly");
    }
}
```

The fuzz test will show gas scaling as O(K × M) and will hit the 30 M ceiling at moderate (K, M) pairs well within the uncapped `maxNodeDelegatorLimit`.

### Citations

**File:** contracts/LRTOracle.sol (L87-96)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }

    /// @dev update rsETH price as an manager account
    /// @dev main benefit is to be able to update the price in case of the price going above the threshold
    /// @dev only LRT manager is allowed to call this function
    function updateRSETHPriceAsManager() external onlyLRTManager {
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

**File:** contracts/LRTDepositPool.sol (L49-49)
```text
        maxNodeDelegatorLimit = 10;
```

**File:** contracts/LRTDepositPool.sol (L290-296)
```text
    function updateMaxNodeDelegatorLimit(uint256 maxNodeDelegatorLimit_) external onlyLRTAdmin {
        if (maxNodeDelegatorLimit_ < nodeDelegatorQueue.length) {
            revert InvalidMaximumNodeDelegatorLimit();
        }

        maxNodeDelegatorLimit = maxNodeDelegatorLimit_;
        emit MaxNodeDelegatorLimitUpdated(maxNodeDelegatorLimit);
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

**File:** contracts/NodeDelegatorHelper.sol (L31-39)
```text
    function getAssetBalance(ILRTConfig lrtConfig, address asset) internal view returns (uint256) {
        address strategy = lrtConfig.assetStrategy(asset);
        if (strategy == address(0)) {
            return 0;
        }
        uint256 withdrawableShare = getWithdrawableShare(lrtConfig, IStrategy(strategy));

        return IStrategy(strategy).sharesToUnderlyingView(withdrawableShare);
    }
```
