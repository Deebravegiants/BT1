### Title
Missing Interface Validation in `addNodeDelegatorContractToQueue` Causes Irrecoverable DoS of Deposits, Withdrawals, and Price Updates - (File: contracts/LRTDepositPool.sol)

### Summary
`addNodeDelegatorContractToQueue` in `LRTDepositPool.sol` does not verify that added addresses implement the `INodeDelegator` interface. If a non-conforming address is added, every call to `getAssetDistributionData()` and `getETHDistributionData()` reverts, freezing all user deposits, rsETH price updates, and withdrawal initiations. Critically, the removal function `_removeNodeDelegatorContractFromQueue` also calls `INodeDelegator` methods on the address being removed, making in-place recovery impossible without a contract upgrade.

### Finding Description
`addNodeDelegatorContractToQueue` performs only a non-zero address check before pushing an address into `nodeDelegatorQueue`:

```solidity
// LRTDepositPool.sol:308-322
for (uint256 i; i < length;) {
    UtilLib.checkNonZeroAddress(nodeDelegatorContracts[i]);
    if (isNodeDelegator[nodeDelegatorContracts[i]] == 0) {
        nodeDelegatorQueue.push(nodeDelegatorContracts[i]);
    }
    isNodeDelegator[nodeDelegatorContracts[i]] = 1;
    ...
}
```

No interface conformance check is performed. [1](#0-0) 

`getAssetDistributionData()` then iterates over every entry in `nodeDelegatorQueue` and calls `INodeDelegator` methods on each:

```solidity
assetStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetBalance(asset);
assetUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset);
``` [2](#0-1) 

`getETHDistributionData()` does the same for ETH-specific methods:

```solidity
ethStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();
ethUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(LRTConstants.ETH_TOKEN);
``` [3](#0-2) 

If any entry in `nodeDelegatorQueue` is a contract that does not implement `INodeDelegator` (e.g., an uninitialized proxy, an EOA-like contract, or a wrong contract address), these calls revert, propagating the revert up through:

- `getTotalAssetDeposits()` → `_beforeDeposit()` → `depositETH()` / `depositAsset()` (all user deposits frozen) [4](#0-3) 
- `LRTOracle._getTotalEthInProtocol()` → `updateRSETHPrice()` (public price update frozen) [5](#0-4) 
- `LRTWithdrawalManager.getAvailableAssetAmount()` → `initiateWithdrawal()` (all withdrawal initiations frozen) [6](#0-5) 

The recovery path is also broken. `_removeNodeDelegatorContractFromQueue` calls `_checkResidueEthBalance`, which calls `INodeDelegator(nodeDelegatorAddress).getEffectivePodShares()` and `getAssetUnstaking()`, and `_checkResidueLSTBalance`, which calls `getAssetBalance()` and `getAssetUnstaking()` on the address being removed:

```solidity
function _checkResidueEthBalance(address nodeDelegatorAddress) internal view {
    if (
        INodeDelegator(nodeDelegatorAddress).getEffectivePodShares() != 0
            || ...
            || INodeDelegator(nodeDelegatorAddress).getAssetUnstaking(LRTConstants.ETH_TOKEN) > 0
    ) { revert NodeDelegatorHasETH(); }
}
``` [7](#0-6) 

If the address does not implement `INodeDelegator`, the removal call also reverts, making it impossible to remove the bad entry without a contract upgrade.

### Impact Explanation
A non-conforming address in `nodeDelegatorQueue` freezes all user-facing protocol functions: deposits, withdrawal initiations, and rsETH price updates. Because the removal mechanism itself calls `INodeDelegator` methods on the address being removed, the bad entry cannot be removed through normal operation. Recovery requires deploying a contract upgrade, during which all user funds are inaccessible. This constitutes **temporary freezing of funds** (Medium), with the duration determined by governance upgrade latency.

### Likelihood Explanation
`addNodeDelegatorContractToQueue` is `onlyLRTAdmin`. An admin could accidentally supply an uninitialized proxy address, a wrong contract address, or an EOA-like contract that does not implement `INodeDelegator`. The absence of any interface validation check makes this misconfiguration more likely than if a conformance check were enforced at registration time. The external report's analogous finding was acknowledged by the client as a realistic concern under the same conditions.

### Recommendation
In `addNodeDelegatorContractToQueue`, add an interface conformance check before pushing the address into `nodeDelegatorQueue`. For example, call a view function on the candidate address and verify it succeeds:

```solidity
// Verify the address implements INodeDelegator
try INodeDelegator(nodeDelegatorContracts[i]).getEffectivePodShares() returns (uint256) {
    // valid
} catch {
    revert InvalidNodeDelegatorAddress(nodeDelegatorContracts[i]);
}
```

This mirrors the pattern already used in `LRTOracle.updatePriceOracleForValidated`, which calls `IPriceFetcher(priceOracle).getAssetPrice(asset)` before accepting the oracle address. [8](#0-7) 

### Proof of Concept
1. Admin calls `addNodeDelegatorContractToQueue([badAddress])` where `badAddress` is a contract that does not implement `INodeDelegator` (e.g., an uninitialized UUPS proxy or a wrong contract).
2. The address passes the `checkNonZeroAddress` check and is pushed into `nodeDelegatorQueue`. [9](#0-8) 
3. Any user calls `depositETH(minAmount, "ref")`.
4. `_beforeDeposit()` calls `getTotalAssetDeposits()` → `getAssetDistributionData()` → `INodeDelegator(badAddress).getAssetBalance(asset)` → **reverts**. All deposits are now DoS'd. [2](#0-1) 
5. Admin attempts recovery via `removeNodeDelegatorContractFromQueue(badAddress)`.
6. `_checkResidueEthBalance(badAddress)` calls `INodeDelegator(badAddress).getEffectivePodShares()` → **reverts**. Removal is impossible. [7](#0-6) 
7. Protocol remains frozen for deposits, price updates, and withdrawal initiations until a contract upgrade is deployed.

### Citations

**File:** contracts/LRTDepositPool.sol (L302-323)
```text
    function addNodeDelegatorContractToQueue(address[] calldata nodeDelegatorContracts) external onlyLRTAdmin {
        uint256 length = nodeDelegatorContracts.length;
        if (nodeDelegatorQueue.length + length > maxNodeDelegatorLimit) {
            revert MaximumNodeDelegatorLimitReached();
        }

        for (uint256 i; i < length;) {
            UtilLib.checkNonZeroAddress(nodeDelegatorContracts[i]);

            // check if node delegator contract is already added and add it if not
            if (isNodeDelegator[nodeDelegatorContracts[i]] == 0) {
                nodeDelegatorQueue.push(nodeDelegatorContracts[i]);
                emit NodeDelegatorAddedinQueue(nodeDelegatorContracts[i]);
            }

            isNodeDelegator[nodeDelegatorContracts[i]] = 1;

            unchecked {
                ++i;
            }
        }
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

**File:** contracts/LRTDepositPool.sol (L447-456)
```text
        for (uint256 i; i < ndcsCount;) {
            assetLyingInNDCs += IERC20(asset).balanceOf(nodeDelegatorQueue[i]);

            assetStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetBalance(asset);
            assetUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset);

            unchecked {
                ++i;
            }
        }
```

**File:** contracts/LRTDepositPool.sol (L484-493)
```text
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

**File:** contracts/LRTDepositPool.sol (L616-624)
```text
    function _checkResidueEthBalance(address nodeDelegatorAddress) internal view {
        if (
            INodeDelegator(nodeDelegatorAddress).getEffectivePodShares() != 0
                || address(nodeDelegatorAddress).balance > maxNegligibleAmount
                || INodeDelegator(nodeDelegatorAddress).getAssetUnstaking(LRTConstants.ETH_TOKEN) > 0
        ) {
            revert NodeDelegatorHasETH();
        }
    }
```

**File:** contracts/LRTOracle.sol (L101-108)
```text
    function updatePriceOracleForValidated(address asset, address priceOracle) external onlyLRTAdmin {
        // Sanity check: oracle price must have precision between 1e16 and 1e19
        uint256 price = IPriceFetcher(priceOracle).getAssetPrice(asset);
        if (price > 1e19 || price < 1e16) {
            revert InvalidPriceOracle();
        }
        updatePriceOracleFor(asset, priceOracle);
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

**File:** contracts/LRTWithdrawalManager.sol (L599-603)
```text
    function getAvailableAssetAmount(address asset) public view override returns (uint256 availableAssetAmount) {
        ILRTDepositPool lrtDepositPool = ILRTDepositPool(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        uint256 totalAssets = lrtDepositPool.getTotalAssetDeposits(asset);
        availableAssetAmount = totalAssets > assetsCommitted[asset] ? totalAssets - assetsCommitted[asset] : 0;
    }
```
