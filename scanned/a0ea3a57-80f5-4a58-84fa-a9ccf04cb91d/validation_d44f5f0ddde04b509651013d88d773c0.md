### Title
Single `maxNegligibleAmount` Threshold Applied Across LST Assets Without Decimal Normalization - (`contracts/LRTDepositPool.sol`)

---

### Summary

`LRTDepositPool._checkResidueLSTBalance()` and `LRTConfig.removeSupportedAsset()` both compare raw token balances against a single `maxNegligibleAmount` value without normalizing for each asset's decimals. If a supported LST with fewer decimals than 18 is ever added, the threshold becomes meaningless for that token, silently bypassing the safety guard and allowing a NodeDelegator or supported asset to be removed while still holding significant user funds.

---

### Finding Description

`LRTDepositPool` stores a single `uint256 public maxNegligibleAmount` used as a universal "dust" threshold across all supported LST assets.

In `_checkResidueLSTBalance()`, the raw balance of each LST token held by a NodeDelegator is compared directly against this threshold:

```solidity
assetBalance = IERC20(supportedAssets[i]).balanceOf(nodeDelegatorAddress)
    + INodeDelegator(nodeDelegatorAddress).getAssetBalance(supportedAssets[i]);
assetBalance += INodeDelegator(nodeDelegatorAddress).getAssetUnstaking(supportedAssets[i]);

if (assetBalance > maxNegligibleAmount) {
    revert NodeDelegatorHasAssetBalance(supportedAssets[i], assetBalance);
}
``` [1](#0-0) 

`assetBalance` is denominated in the token's own native decimals. There is no normalization step. The same `maxNegligibleAmount` is also used in `LRTConfig.removeSupportedAsset()`:

```solidity
if (ILRTDepositPool(depositPool).getTotalAssetDeposits(asset) > maxNegligibleAmount) {
    revert CannotRemoveAssetWithDeposits(asset);
}
``` [2](#0-1) 

`getTotalAssetDeposits(asset)` returns the sum of all protocol-held balances in the token's native decimals. [3](#0-2) 

`maxNegligibleAmount` is a single shared value with no per-asset decimal awareness. [4](#0-3) [5](#0-4) 

---

### Impact Explanation

Suppose `maxNegligibleAmount` is set to `1e15` (a reasonable dust threshold for 18-decimal ETH LSTs, representing ~0.001 ETH). If a 6-decimal LST is later added as a supported asset:

- `1e15` in 6-decimal units equals **1,000,000,000 tokens** — an astronomically large amount.
- The check `assetBalance > maxNegligibleAmount` will **never** trigger for any realistic 6-decimal balance.
- `_removeNodeDelegatorContractFromQueue` will succeed even when the NodeDelegator holds substantial user funds in the 6-decimal token, because `_checkResidueLSTBalance` silently passes.
- Once removed from `nodeDelegatorQueue`, the NodeDelegator is no longer tracked by the protocol. User funds held in it become inaccessible through normal protocol flows — **temporary (potentially permanent) freezing of funds**.

The inverse also holds: if `maxNegligibleAmount` is calibrated for a 6-decimal token, any 18-decimal LST balance will always exceed it, permanently blocking NodeDelegator removal.

**Impact: Medium — Temporary freezing of funds.**

---

### Likelihood Explanation

The current supported assets (stETH, ETHx) are all 18-decimal, so the bug is dormant today. However, `addNewSupportedAsset` is callable by the `TIME_LOCK_ROLE` and places no restriction on token decimals. The protocol is explicitly designed to support multiple LST assets. A future governance decision to add a non-18-decimal LST (e.g., a rebasing token with 6 or 8 decimals) would activate this vulnerability without any code change. The admin removing the NodeDelegator acts in good faith — the check passes without warning.

**Likelihood: Low** (requires addition of a non-18-decimal supported asset).

---

### Recommendation

Normalize `assetBalance` to a common precision (e.g., 18 decimals) before comparing against `maxNegligibleAmount` in both `_checkResidueLSTBalance` and `LRTConfig.removeSupportedAsset`. Alternatively, maintain a per-asset negligible threshold mapping (keyed by asset address) so each token's dust threshold is expressed in its own native decimals.

```solidity
// Example normalization in _checkResidueLSTBalance:
uint8 decimals = IERC20Metadata(supportedAssets[i]).decimals();
uint256 normalizedBalance = assetBalance * (10 ** (18 - decimals));
if (normalizedBalance > maxNegligibleAmount) {
    revert NodeDelegatorHasAssetBalance(supportedAssets[i], assetBalance);
}
```

---

### Proof of Concept

1. Admin calls `LRTConfig.addNewSupportedAsset(sixDecimalLST, depositLimit)` — adds a 6-decimal LST.
2. Users deposit the 6-decimal LST via `LRTDepositPool.depositAsset(sixDecimalLST, ...)`.
3. Operator transfers the 6-decimal LST to a NodeDelegator via `transferAssetToNodeDelegator`.
4. `maxNegligibleAmount` is `1e15` (set for 18-decimal tokens).
5. Admin calls `removeNodeDelegatorContractFromQueue(ndcAddress)`.
6. `_checkResidueLSTBalance` computes `assetBalance` for `sixDecimalLST` — e.g., `500_000` (0.5 tokens in 6-decimal = $0.50 USDC equivalent, but also could be `500_000_000` = $500).
7. `500_000_000 > 1e15` → **false** → check passes silently.
8. NodeDelegator is removed from the queue. The 6-decimal LST balance inside it is now unreachable through normal protocol operations. [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/LRTDepositPool.sol (L35-36)
```text
    /// @notice maximum amount that can be ignored
    uint256 public maxNegligibleAmount;
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

**File:** contracts/LRTDepositPool.sol (L579-597)
```text
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

**File:** contracts/LRTDepositPool.sol (L626-645)
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
```

**File:** contracts/LRTConfig.sol (L30-30)
```text
    uint256 public maxNegligibleAmount;
```

**File:** contracts/LRTConfig.sol (L82-84)
```text
        if (ILRTDepositPool(depositPool).getTotalAssetDeposits(asset) > maxNegligibleAmount) {
            revert CannotRemoveAssetWithDeposits(asset);
        }
```
