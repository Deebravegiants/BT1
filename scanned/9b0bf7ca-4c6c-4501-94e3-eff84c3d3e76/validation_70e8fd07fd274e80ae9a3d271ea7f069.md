### Title
stETH Stranded in L1Vault After `unwrapWstETH()` When stETH Support Is Removed From LRTConfig — (`contracts/external/lido/IWstETH.sol`, `contracts/L1Vault.sol`, `contracts/L1VaultV2.sol`)

---

### Summary

After `unwrapWstETH()` irreversibly converts wstETH → stETH in the vault, if an admin legitimately removes stETH from `LRTConfig`'s supported assets (e.g., during a migration), `depositAssetForL1Vault(stETH)` will revert with `AssetNotSupported`. The `IWstETH` interface exposes only `unwrap()` — no `wrap()` — so the vault has no on-chain path to re-wrap the stETH. The stETH is frozen in the vault until governance re-adds stETH support.

---

### Finding Description

**Step 1 — Irreversible unwrap.**
`unwrapWstETH()` calls `IWstETH(wstETH).unwrap(wstETHBalance)`, burning all wstETH and crediting stETH to the vault. [1](#0-0) [2](#0-1) 

The `IWstETH` interface declares only `unwrap()`; there is no `wrap()` method, so the vault cannot re-wrap stETH back to wstETH through any existing function.

**Step 2 — Guard in `removeSupportedAsset` does not cover L1Vault.**
`LRTConfig.removeSupportedAsset()` checks `getTotalAssetDeposits(asset)` before allowing removal: [3](#0-2) 

`getTotalAssetDeposits` aggregates balances from the DepositPool, NDCs, EigenLayer, the Converter, and the UnstakingVault — but **not** from L1Vault. [4](#0-3) 

Therefore, if stETH is sitting exclusively in L1Vault (post-unwrap), the guard passes and the admin can successfully remove stETH from supported assets.

**Step 3 — `depositAssetForL1Vault(stETH)` reverts.**
`depositAsset` in `LRTDepositPool` is gated by `onlySupportedERC20Token(asset)`: [5](#0-4) [6](#0-5) 

With stETH de-listed, every call to `depositAssetForL1Vault(stETH)` reverts with `AssetNotSupported`, blocking the entire wstETH → stETH → rsETH → L2 pipeline. [7](#0-6) 

**Step 4 — No recovery path within the vault.**
The vault has no `wrap()` call, no emergency token-rescue function, and no alternative deposit path for stETH. Recovery requires a governance action to re-add stETH via `addNewSupportedAsset` (requires `TIME_LOCK_ROLE`), which introduces a time-delayed operational gap. [8](#0-7) 

---

### Impact Explanation

stETH is temporarily frozen in L1Vault. Its value is not lost (stETH accrues yield in place), but the protocol fails to deliver the promised rsETH to L2 users for the duration of the freeze. This matches **Low — Contract fails to deliver promised returns, but doesn't lose value**.

---

### Likelihood Explanation

The scenario requires two sequential, role-gated actions by trusted parties:
1. `MANAGER_ROLE` calls `unwrapWstETH()`.
2. `DEFAULT_ADMIN_ROLE` calls `removeSupportedAsset(stETH, ...)` — a legitimate governance action during a migration or asset-list update.

The admin is not acting maliciously; the `removeSupportedAsset` guard simply does not account for L1Vault balances, making this a realistic operational mistake. Likelihood is **low-to-medium** given that migrations are infrequent but the guard gap is silent and non-obvious.

---

### Recommendation

1. **Extend the `removeSupportedAsset` guard** to also query L1Vault balances for the asset being removed, or add a dedicated check that reverts if any registered L1Vault holds a non-negligible balance of the asset.
2. **Add a `wrapStETH()` function** to L1Vault/L1VaultV2 that calls the real wstETH `wrap(uint256)` (extend `IWstETH` to include `wrap()`), providing a reversal path if the deposit pipeline is blocked.
3. **Add a token-rescue / emergency-withdrawal function** (admin-only) so that stranded ERC-20 tokens can be recovered without requiring governance to re-add asset support.

---

### Proof of Concept

```solidity
// 1. Manager unwraps wstETH → stETH lands in L1Vault
l1Vault.unwrapWstETH(); // IWstETH.unwrap() burns wstETH, credits stETH

// 2. Admin removes stETH from LRTConfig
//    Guard passes because getTotalAssetDeposits(stETH) == 0
//    (L1Vault balance is not counted)
lrtConfig.removeSupportedAsset(stETH, stETHIndex);

// 3. Manager tries to convert stETH → rsETH
//    Reverts: LRTDepositPool.depositAsset has onlySupportedERC20Token(stETH)
//    → ILRTConfig.AssetNotSupported()
l1Vault.depositAssetForL1Vault(stETH); // REVERTS

// 4. No wrap() available in IWstETH → stETH stuck in vault
//    Recovery only via governance re-adding stETH (TIME_LOCK_ROLE delay)
```

### Citations

**File:** contracts/L1Vault.sol (L166-182)
```text
    function depositAssetForL1Vault(address token) external nonReentrant onlyRole(MANAGER_ROLE) {
        UtilLib.checkNonZeroAddress(token);

        uint256 tokenBalance = IERC20(token).balanceOf(address(this));
        uint256 rsETHAmountToMint = lrtDepositPool.getRsETHAmountToMint(token, tokenBalance);

        if (rsETHAmountToMint == 0) {
            revert InvalidMinRSETHAmountExpected();
        }

        // Approve the LRT deposit pool to transfer the token
        IERC20(token).safeIncreaseAllowance(address(lrtDepositPool), tokenBalance);

        lrtDepositPool.depositAsset(token, tokenBalance, rsETHAmountToMint, "");

        emit AssetDepositForL1Vault(token, tokenBalance, rsETHAmountToMint);
    }
```

**File:** contracts/L1Vault.sol (L185-196)
```text
    function unwrapWstETH() external nonReentrant onlyRole(MANAGER_ROLE) {
        uint256 wstETHBalance = IERC20(wstETH).balanceOf(address(this));

        if (wstETHBalance == 0) {
            revert NoWstETHBalance();
        }

        // Unwrap wstETH to stETH
        uint256 stETHAmount = IWstETH(wstETH).unwrap(wstETHBalance);

        emit WstETHUnwrapped(stETHAmount);
    }
```

**File:** contracts/external/lido/IWstETH.sol (L8-18)
```text
interface IWstETH {
    /**
     * @notice Exchanges wstETH to stETH
     * @param _wstETHAmount amount of wstETH to uwrap in exchange for stETH
     * @dev Requirements:
     *  - `_wstETHAmount` must be non-zero
     *  - msg.sender must have at least `_wstETHAmount` wstETH.
     * @return Amount of stETH user receives after unwrap
     */
    function unwrap(uint256 _wstETHAmount) external returns (uint256);
}
```

**File:** contracts/LRTConfig.sol (L80-84)
```text
        address depositPool = getContract(LRTConstants.LRT_DEPOSIT_POOL);

        if (ILRTDepositPool(depositPool).getTotalAssetDeposits(asset) > maxNegligibleAmount) {
            revert CannotRemoveAssetWithDeposits(asset);
        }
```

**File:** contracts/LRTConfig.sol (L99-101)
```text
    function addNewSupportedAsset(address asset, uint256 depositLimit) external onlyRole(LRTConstants.TIME_LOCK_ROLE) {
        _addNewSupportedAsset(asset, depositLimit);
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

**File:** contracts/utils/LRTConfigRoleChecker.sol (L72-80)
```text
    modifier onlySupportedERC20Token(address asset) {
        if (!lrtConfig.isSupportedAsset(asset)) {
            revert ILRTConfig.AssetNotSupported();
        }
        if (asset == LRTConstants.ETH_TOKEN) {
            revert ILRTConfig.ETHNotSupported();
        }
        _;
    }
```
