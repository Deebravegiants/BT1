### Title
Users Cannot Initiate Withdrawals for Assets Without a Strategy Set - (`contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTWithdrawalManager.initiateWithdrawal` enforces `onlySupportedStrategy(asset)`, which reverts when `lrtConfig.assetStrategy(asset) == address(0)`. However, `LRTDepositPool.depositAsset` has no equivalent strategy check. This asymmetry means users can deposit an asset that has no EigenLayer strategy configured and receive rsETH, but they are permanently blocked from initiating a withdrawal for that asset until a strategy is set — directly mirroring the Derby inactive-vault withdrawal freeze.

---

### Finding Description

`LRTConfig.addNewSupportedAsset` adds an asset to `isSupportedAsset` and `supportedAssetList` but does **not** set `assetStrategy[asset]`, leaving it as `address(0)`. [1](#0-0) 

`LRTDepositPool.depositAsset` only applies `onlySupportedERC20Token(asset)`, which checks `isSupportedAsset[asset]` and that the asset is not ETH — no strategy check. [2](#0-1) 

`LRTWithdrawalManager.initiateWithdrawal` applies **both** `onlySupportedAsset(asset)` and `onlySupportedStrategy(asset)`: [3](#0-2) 

The `onlySupportedStrategy` modifier reverts with `StrategyNotSupported` whenever `assetStrategy[asset] == address(0)` for any non-ETH asset: [4](#0-3) 

The result is a deposit/withdrawal asymmetry: a user who deposits a newly-added asset (before its strategy is configured) receives rsETH, but every subsequent call to `initiateWithdrawal` for that asset reverts. The user's rsETH is stranded — it cannot be redeemed for the deposited asset until an admin sets a strategy via `updateAssetStrategy`.

`updateAssetStrategy` itself requires `UtilLib.checkNonZeroAddress(strategy)`, so there is no way for the strategy to be set to zero after it is first assigned; the only path to `assetStrategy[asset] == address(0)` for a live asset is the window between `addNewSupportedAsset` and the first `updateAssetStrategy` call. [5](#0-4) 

---

### Impact Explanation

Users who deposit a newly-listed asset during the strategy-configuration window receive rsETH but cannot call `initiateWithdrawal` for that asset. Their rsETH is backed by the deposited asset but the withdrawal entry-point is gated behind a condition they cannot satisfy. This constitutes a **temporary freezing of funds** (Medium severity) that persists until an admin configures the strategy. If the admin delays or the asset is deprecated before a strategy is ever set, the freeze becomes indefinite.

---

### Likelihood Explanation

The scenario is operationally realistic. New assets are added via `addNewSupportedAsset` (TIME_LOCK_ROLE) as a separate governance step from strategy configuration (`updateAssetStrategy`, DEFAULT_ADMIN_ROLE). There is no on-chain enforcement preventing deposits in the gap between these two transactions. Any user who deposits during this window is affected without any malicious action required.

---

### Recommendation

Add the `onlySupportedStrategy(asset)` check to `LRTDepositPool.depositAsset` so that deposits are only accepted for assets that already have a strategy configured, eliminating the asymmetry. Alternatively, remove `onlySupportedStrategy` from `initiateWithdrawal` and instead gate only the `unlockQueue` operator path on strategy presence, so that users can always queue a withdrawal regardless of strategy state.

---

### Proof of Concept

1. Admin calls `LRTConfig.addNewSupportedAsset(tokenX, depositLimit)` — `isSupportedAsset[tokenX] = true`, `assetStrategy[tokenX] = address(0)`. [6](#0-5) 

2. Alice calls `LRTDepositPool.depositAsset(tokenX, amount, minRSETH, "")` — passes `onlySupportedERC20Token`, rsETH is minted to Alice. [2](#0-1) 

3. Alice calls `LRTWithdrawalManager.initiateWithdrawal(tokenX, rsETHAmount, "")` — execution reaches `onlySupportedStrategy(tokenX)`, which evaluates `lrtConfig.assetStrategy(tokenX) == address(0)` → `true` → reverts with `StrategyNotSupported`. [4](#0-3) 

4. Alice's rsETH is locked in `LRTWithdrawalManager` (transferred in at line 166) — wait, actually rsETH is transferred in only after the modifier passes. The rsETH stays in Alice's wallet but she cannot queue a withdrawal for `tokenX` at all. Her deposited `tokenX` value is locked in the protocol with no withdrawal path until admin acts. [7](#0-6)

### Citations

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

**File:** contracts/LRTWithdrawalManager.sol (L150-170)
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
            revert InvalidAmountToWithdraw();
        }

        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();
```
