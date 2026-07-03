### Title
Dust LST Deposit Permanently Blocks NodeDelegator Removal When `maxNegligibleAmount` Is Zero - (File: contracts/LRTDepositPool.sol)

### Summary
When `maxNegligibleAmount` is zero (its default uninitialized value), any unprivileged user can send 1 wei of any supported LST token directly to a NodeDelegator contract address, causing `_checkResidueLSTBalance` to revert and permanently blocking that NodeDelegator's removal from the queue until admin intervention.

### Finding Description
`_removeNodeDelegatorContractFromQueue` calls `_checkResidueLSTBalance`, which iterates over all supported assets and reverts if any asset balance exceeds `maxNegligibleAmount`:

```solidity
assetBalance = IERC20(supportedAssets[i]).balanceOf(nodeDelegatorAddress)
    + INodeDelegator(nodeDelegatorAddress).getAssetBalance(supportedAssets[i]);
assetBalance += INodeDelegator(nodeDelegatorAddress).getAssetUnstaking(supportedAssets[i]);

if (assetBalance > maxNegligibleAmount) {
    revert NodeDelegatorHasAssetBalance(supportedAssets[i], assetBalance);
}
```

`maxNegligibleAmount` is declared as a storage variable but is **never initialized** in `initialize()`, so it defaults to `0`. With `maxNegligibleAmount == 0`, the condition `assetBalance > 0` means any 1-wei ERC20 balance — trivially deposited by any external caller via a standard `IERC20.transfer()` — causes the removal to revert. The same pattern applies to the ETH residue check in `_checkResidueEthBalance` for `address(nodeDelegatorAddress).balance > maxNegligibleAmount`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

### Impact Explanation
A NodeDelegator that cannot be removed from the queue remains in the `nodeDelegatorQueue` array indefinitely. This has two concrete consequences:

1. **Operational freeze**: If a NodeDelegator must be urgently decommissioned (e.g., its operator key is compromised, or it has been force-undelegated by EigenLayer), the admin cannot remove it from the queue. Funds delegated through that NodeDelegator remain under its control and cannot be cleanly migrated to a replacement NodeDelegator.
2. **Accounting pollution**: The stuck NodeDelegator continues to be iterated in `getTotalAssetDeposits` and `getAssetDistributionData`, inflating or distorting the reported total assets and the rsETH exchange rate computed by `LRTOracle._getTotalEthInProtocol`.

This maps to **Medium — Temporary freezing of funds**: the inability to remove a compromised NodeDelegator temporarily traps assets under its control until the admin calls `setMaxNegligibleAmount` with a non-zero value. [5](#0-4) [6](#0-5) 

### Likelihood Explanation
The attack requires only a single ERC20 `transfer` of 1 wei of any supported LST (stETH, ETHx) to the target NodeDelegator address. This costs negligible gas and no meaningful capital. The default value of `maxNegligibleAmount` is `0` because it is never set in `initialize()`, making every fresh deployment vulnerable until the admin explicitly calls `setMaxNegligibleAmount`. Any unprivileged depositor or external observer who knows the NodeDelegator address can execute this. [7](#0-6) [8](#0-7) 

### Recommendation
Initialize `maxNegligibleAmount` to a sensible non-zero dust threshold (e.g., `1e6` wei) inside `initialize()`, so that the residue checks are `assetBalance > dustThreshold` rather than `assetBalance > 0`. This mirrors the short-term recommendation in the external report: treat economically insignificant balances as inactive when evaluating whether a position is "empty."

```solidity
function initialize(address lrtConfigAddr) external initializer {
    ...
    maxNegligibleAmount = 1e6; // initialize to a dust threshold
    ...
}
```

### Proof of Concept
1. Protocol deploys `LRTDepositPool`; `maxNegligibleAmount` is `0` (default).
2. Admin adds `NodeDelegator_A` to the queue via `addNodeDelegatorContractToQueue`.
3. Attacker calls `IERC20(stETH).transfer(address(NodeDelegator_A), 1)` — costs ~1 wei of stETH.
4. Admin attempts `removeNodeDelegatorContractFromQueue(NodeDelegator_A)`.
5. Inside `_checkResidueLSTBalance`: `assetBalance = 1 > maxNegligibleAmount (= 0)` → `revert NodeDelegatorHasAssetBalance(stETH, 1)`.
6. Removal is permanently blocked. Admin must call `setMaxNegligibleAmount(1)` first to unblock, but this also permanently relaxes the dust threshold for all future removals. [9](#0-8) [10](#0-9)

### Citations

**File:** contracts/LRTDepositPool.sol (L36-36)
```text
    uint256 public maxNegligibleAmount;
```

**File:** contracts/LRTDepositPool.sol (L44-52)
```text
    /// @param lrtConfigAddr LRT config address
    function initialize(address lrtConfigAddr) external initializer {
        UtilLib.checkNonZeroAddress(lrtConfigAddr);
        __Pausable_init();
        __ReentrancyGuard_init();
        maxNodeDelegatorLimit = 10;
        lrtConfig = ILRTConfig(lrtConfigAddr);
        emit UpdatedLRTConfig(lrtConfigAddr);
    }
```

**File:** contracts/LRTDepositPool.sol (L271-277)
```text
    /// @notice maximum amount that can be ignored
    /// @dev only callable by LRT admin
    /// @param maxNegligibleAmount_ Maximum amount that can be ignored
    function setMaxNegligibleAmount(uint256 maxNegligibleAmount_) external onlyLRTAdmin {
        maxNegligibleAmount = maxNegligibleAmount_;
        emit MaxNegligibleAmountUpdated(maxNegligibleAmount_);
    }
```

**File:** contracts/LRTDepositPool.sol (L325-330)
```text
    /// @notice remove node delegator contract address from queue
    /// @dev only callable by LRT admin
    /// @param nodeDelegatorAddress NodeDelegator contract address
    function removeNodeDelegatorContractFromQueue(address nodeDelegatorAddress) external onlyLRTAdmin {
        _removeNodeDelegatorContractFromQueue(nodeDelegatorAddress);
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

**File:** contracts/LRTDepositPool.sol (L577-597)
```text
    /// @notice internal function to remove node delegator contract address from queue
    /// @param nodeDelegatorAddress NodeDelegator contract address
    function _removeNodeDelegatorContractFromQueue(address nodeDelegatorAddress) internal {
        // 1. check if node delegator contract is in queue and find Index
        uint256 ndcIndex = _getNDCIndex(nodeDelegatorAddress);

        // 2. revert if node delegator contract has any asset balances.
        // 2.1 check if NDC has native ETH balance in eigen layer or/and in itself.
        _checkResidueEthBalance(nodeDelegatorAddress);
        // 2.2  check if NDC has LST balance
        _checkResidueLSTBalance(nodeDelegatorAddress);

        // 3. remove node delegator contract from queue
        // 3.1 remove from isNodeDelegator mapping
        isNodeDelegator[nodeDelegatorAddress] = 0;
        // 3.2 remove from nodeDelegatorQueue
        nodeDelegatorQueue[ndcIndex] = nodeDelegatorQueue[nodeDelegatorQueue.length - 1];
        nodeDelegatorQueue.pop();

        emit NodeDelegatorRemovedFromQueue(nodeDelegatorAddress);
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

**File:** contracts/LRTDepositPool.sol (L626-646)
```text
    /// @dev reverts if NDC has LST balance
    function _checkResidueLSTBalance(address nodeDelegatorAddress) internal view {
        address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
        uint256 supportedAssetsLength = supportedAssets.length;

        uint256 assetBalance;
        for (uint256 i; i < supportedAssetsLength; ++i) {
            if (supportedAssets[i] == LRTConstants.ETH_TOKEN) {
                // this function only checks for residual LST balance
                continue;
            }

            assetBalance = IERC20(supportedAssets[i]).balanceOf(nodeDelegatorAddress)
                + INodeDelegator(nodeDelegatorAddress).getAssetBalance(supportedAssets[i]);
            assetBalance += INodeDelegator(nodeDelegatorAddress).getAssetUnstaking(supportedAssets[i]);

            if (assetBalance > maxNegligibleAmount) {
                revert NodeDelegatorHasAssetBalance(supportedAssets[i], assetBalance);
            }
        }
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
