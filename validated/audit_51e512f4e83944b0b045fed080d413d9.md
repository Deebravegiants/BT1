### Title
`_setContract()` Can Override Active Protocol Contracts Without Checking Existing State, Causing TVL Mis-accounting and Potential Protocol Freeze - (File: contracts/LRTConfig.sol)

### Summary
`LRTConfig._setContract()` allows overriding critical contract registry entries (e.g., `LRT_UNSTAKING_VAULT`) without verifying whether the existing contract holds active user funds. If overridden during a protocol upgrade while the old vault holds assets, those assets are silently excluded from TVL accounting, causing rsETH price to drop and potentially triggering the automatic price-protection pause.

### Finding Description
`_setContract()` in `LRTConfig.sol` performs only a same-value guard:

```solidity
// contracts/LRTConfig.sol lines 244-251
function _setContract(bytes32 key, address val) private {
    UtilLib.checkNonZeroAddress(val);
    if (contractMap[key] == val) {
        revert ValueAlreadyInUse();
    }
    contractMap[key] = val;
    emit SetContract(key, val);
}
```

It does **not** verify whether the existing contract has active user funds before overwriting the mapping entry. This is in direct contrast to `updateAssetStrategy()`, which was explicitly hardened with exactly this kind of guard:

```solidity
// contracts/LRTConfig.sol lines 150-167
if (assetStrategy[asset] != address(0)) {
    address[] memory ndcs = ILRTDepositPool(depositPool).getNodeDelegatorQueue();
    for (uint256 i = 0; i < length;) {
        uint256 ndcBalance = IStrategy(assetStrategy[asset]).userUnderlyingView(ndcs[i]);
        if (ndcBalance > 0) {
            revert CannotUpdateStrategyAsItHasFundsNDCFunds(ndcs[i], ndcBalance);
        }
        ...
    }
}
```

The inconsistency is the root cause: `updateAssetStrategy` was protected against override-while-funded, but `_setContract` was not.

`LRTDepositPool.getAssetDistributionData()` and `getETHDistributionData()` both resolve the unstaking vault address dynamically at call time via `lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT)`:

```solidity
// contracts/LRTDepositPool.sol lines 458-461
address lrtUnstakingVault = lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT);
assetLyingUnstakingVault = IERC20(asset).balanceOf(lrtUnstakingVault);
```

```solidity
// contracts/LRTDepositPool.sol lines 495-496
address lrtUnstakingVault = lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT);
ethLyingInUnstakingVault = lrtUnstakingVault.balance;
```

If `LRT_UNSTAKING_VAULT` is overridden with a new (empty) address, all assets held in the old vault are immediately excluded from `getTotalAssetDeposits()` and therefore from `_getTotalEthInProtocol()` in `LRTOracle`, which feeds directly into rsETH price computation.

### Impact Explanation
When `LRT_UNSTAKING_VAULT` is overridden while the old vault holds user assets:

1. `_getTotalEthInProtocol()` in `LRTOracle` underreports total ETH, computing a lower `newRsETHPrice`.
2. If the price drop exceeds `pricePercentageLimit` relative to `highestRsethPrice`, `_updateRsETHPrice()` automatically pauses `LRTDepositPool` and `LRTWithdrawalManager`, freezing all deposits and withdrawals for all users.
3. Even without hitting the threshold, rsETH holders who redeem during the window receive less ETH than they are entitled to — a direct share/asset mis-accounting loss.

Impact classification: **Medium — Temporary freezing of funds** (price-protection auto-pause) and **Low — Contract fails to deliver promised returns** (rsETH undervalued during the window).

### Likelihood Explanation
The trigger is an admin (`DEFAULT_ADMIN_ROLE`) calling `setContract()` to upgrade `LRT_UNSTAKING_VAULT` to a new implementation while the old vault still holds queued withdrawal assets. This is a realistic operational scenario during protocol upgrades, not a malicious action — exactly analogous to the original report where an admin accidentally adds a vester with a duplicate timeframe. No attacker action is required; the damage occurs the moment the admin transaction is confirmed.

### Recommendation
Mirror the guard already present in `updateAssetStrategy()`. Before overwriting a contract key that corresponds to a fund-holding contract (e.g., `LRT_UNSTAKING_VAULT`, `LRT_WITHDRAW_MANAGER`), verify that the existing contract holds no active user assets:

```solidity
function _setContract(bytes32 key, address val) private {
    UtilLib.checkNonZeroAddress(val);
    if (contractMap[key] == val) revert ValueAlreadyInUse();
    // For fund-holding contracts, require zero balance before override
    if (key == LRTConstants.LRT_UNSTAKING_VAULT && contractMap[key] != address(0)) {
        require(contractMap[key].balance == 0, "Vault has active ETH");
        // also check LST balances for each supported asset
    }
    contractMap[key] = val;
    emit SetContract(key, val);
}
```

Alternatively, enforce a two-step migration: drain the old vault before registering the new one.

### Proof of Concept
1. Users deposit ETH/LSTs and initiate withdrawals; assets accumulate in `LRT_UNSTAKING_VAULT` (e.g., 1 000 ETH).
2. Admin deploys a new vault implementation and calls `setContract(LRTConstants.LRT_UNSTAKING_VAULT, newVaultAddress)`.
3. `_setContract()` passes (new address ≠ old address) and overwrites `contractMap[LRT_UNSTAKING_VAULT]`.
4. `LRTOracle._updateRsETHPrice()` → `_getTotalEthInProtocol()` → `LRTDepositPool.getETHDistributionData()` now reads `newVaultAddress.balance == 0`; the 1 000 ETH in the old vault is invisible.
5. `newRsETHPrice` drops by the fraction `1000 ETH / totalETH`. If this exceeds `pricePercentageLimit`, `_updateRsETHPrice()` executes the auto-pause branch, freezing all user deposits and withdrawals.
6. Users who redeemed rsETH between steps 3 and 5 received fewer ETH than owed.

**Relevant code references:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/LRTConfig.sol (L150-167)
```text
        // if strategy is already set, check if it has any funds
        if (assetStrategy[asset] != address(0)) {
            // get ndcs
            address depositPool = getContract(LRTConstants.LRT_DEPOSIT_POOL);
            address[] memory ndcs = ILRTDepositPool(depositPool).getNodeDelegatorQueue();

            uint256 length = ndcs.length;
            for (uint256 i = 0; i < length;) {
                uint256 ndcBalance = IStrategy(assetStrategy[asset]).userUnderlyingView(ndcs[i]);
                if (ndcBalance > 0) {
                    revert CannotUpdateStrategyAsItHasFundsNDCFunds(ndcs[i], ndcBalance);
                }

                unchecked {
                    ++i;
                }
            }
        }
```

**File:** contracts/LRTConfig.sol (L244-251)
```text
    function _setContract(bytes32 key, address val) private {
        UtilLib.checkNonZeroAddress(val);
        if (contractMap[key] == val) {
            revert ValueAlreadyInUse();
        }
        contractMap[key] = val;
        emit SetContract(key, val);
    }
```

**File:** contracts/LRTDepositPool.sol (L458-461)
```text
        address lrtUnstakingVault = lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT);

        assetLyingInConverter = 0; // assets in converter are accounted in their eth value => getETHDistributionData()
        assetLyingUnstakingVault = IERC20(asset).balanceOf(lrtUnstakingVault);
```

**File:** contracts/LRTDepositPool.sol (L495-496)
```text
        address lrtUnstakingVault = lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT);
        ethLyingInUnstakingVault = lrtUnstakingVault.balance;
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
