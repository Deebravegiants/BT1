### Title
Missing Strategy Validation on Asset Addition Allows Deposits but Permanently Blocks Withdrawals Until Admin Intervention - (File: contracts/LRTConfig.sol / contracts/LRTWithdrawalManager.sol)

### Summary
`LRTConfig.addNewSupportedAsset()` enables deposits for a new LST immediately, but `LRTWithdrawalManager.initiateWithdrawal()` requires `assetStrategy[asset] != address(0)` for the same asset. Because `assetStrategy` is never set by `addNewSupportedAsset()` and defaults to `address(0)`, any user who deposits a newly added LST before the admin separately calls `updateAssetStrategy()` will find their deposited assets frozen in the protocol.

### Finding Description

`LRTConfig.addNewSupportedAsset()` only sets `isSupportedAsset[asset] = true` and `depositLimitByAsset[asset]`: [1](#0-0) 

`LRTDepositPool.depositAsset()` gates on `onlySupportedERC20Token(asset)`, which checks only `isSupportedAsset`: [2](#0-1) 

`LRTWithdrawalManager.initiateWithdrawal()` additionally gates on `onlySupportedStrategy(asset)`: [3](#0-2) [4](#0-3) 

The `onlySupportedStrategy` modifier reverts for any non-ETH asset whose `assetStrategy` is `address(0)`: [3](#0-2) 

`updateAssetStrategy()` is a completely separate admin call that must be made after `addNewSupportedAsset()`: [5](#0-4) 

This asymmetry is present from the very first deployment: `LRTConfig.initialize()` adds stETH and ethX as supported assets but sets no strategy for either: [6](#0-5) 

### Impact Explanation

Any LST deposited into `LRTDepositPool` while `assetStrategy[asset] == address(0)` is immediately locked. The deposited tokens accumulate in the deposit pool and node delegators. The user receives rsETH but cannot redeem it for the deposited asset via `initiateWithdrawal` — the call reverts with `StrategyNotSupported`. The funds remain frozen until the admin separately calls `updateAssetStrategy`. This matches **Medium — Temporary freezing of funds**.

### Likelihood Explanation

The protocol's own initialization (`LRTConfig.initialize`) adds two assets without strategies, creating the vulnerable window from block 0. Any future `addNewSupportedAsset` call repeats the same pattern. The admin must remember to issue a second, separate transaction (`updateAssetStrategy`) before users deposit. Given that deposits are open immediately after `addNewSupportedAsset`, users can and will deposit during this window. The oversight is realistic and the window is externally observable on-chain.

### Recommendation

Combine asset addition and strategy assignment into a single atomic operation, or add a guard in `depositAsset` that rejects deposits for assets with no strategy set:

```solidity
// Option A: require strategy at asset-add time
function addNewSupportedAsset(address asset, uint256 depositLimit, address strategy) external ...

// Option B: guard in depositAsset
if (lrtConfig.assetStrategy(asset) == address(0)) revert StrategyNotSet();
```

### Proof of Concept

1. Admin calls `LRTConfig.addNewSupportedAsset(newLST, 100_000 ether)` — `isSupportedAsset[newLST] = true`, `assetStrategy[newLST] = address(0)`.
2. User calls `LRTDepositPool.depositAsset(newLST, 10 ether, minRSETH, "")` — passes `onlySupportedERC20Token`, succeeds, user receives rsETH, 10 ether of `newLST` sits in the deposit pool.
3. User calls `LRTWithdrawalManager.initiateWithdrawal(newLST, rsETHAmount, "")` — `onlySupportedStrategy` fires: `lrtConfig.assetStrategy(newLST) == address(0)` → **reverts `StrategyNotSupported`**.
4. The 10 ether of `newLST` is frozen in the protocol. The user's rsETH is not burned (revert before transfer), but the underlying LST cannot be reclaimed until the admin calls `LRTConfig.updateAssetStrategy(newLST, strategyAddr)`.

### Citations

**File:** contracts/LRTConfig.sol (L49-62)
```text
    function initialize(address admin, address stETH, address ethX, address rsETH_) external initializer {
        UtilLib.checkNonZeroAddress(admin);
        UtilLib.checkNonZeroAddress(rsETH_);

        __AccessControl_init();
        _setToken(LRTConstants.ST_ETH_TOKEN, stETH);
        _setToken(LRTConstants.ETHX_TOKEN, ethX);
        _addNewSupportedAsset(stETH, 100_000 ether);
        _addNewSupportedAsset(ethX, 100_000 ether);

        _grantRole(DEFAULT_ADMIN_ROLE, admin);

        rsETH = rsETH_;
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

**File:** contracts/LRTConfig.sol (L138-171)
```text
    function updateAssetStrategy(
        address asset,
        address strategy
    )
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
        onlySupportedAsset(asset)
    {
        UtilLib.checkNonZeroAddress(strategy);
        if (assetStrategy[asset] == strategy) {
            revert ValueAlreadyInUse();
        }
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

        assetStrategy[asset] = strategy;
        emit AssetStrategyUpdate(asset, strategy);
    }
```

**File:** contracts/LRTDepositPool.sol (L99-118)
```text
    function depositAsset(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedERC20Token(asset)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);

        emit AssetDeposit(msg.sender, asset, depositAmount, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L71-76)
```text
    modifier onlySupportedStrategy(address asset) {
        if (asset != LRTConstants.ETH_TOKEN && lrtConfig.assetStrategy(asset) == address(0)) {
            revert StrategyNotSupported();
        }
        _;
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L150-162)
```text
    function initiateWithdrawal(
        address asset,
        uint256 rsETHUnstaked,
        string calldata referralId
    )
        external
        override
        nonReentrant
        whenNotPaused
        onlySupportedAsset(asset)
        onlySupportedStrategy(asset)
    {
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
```
