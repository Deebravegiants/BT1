The code path is fully traceable and confirmed. Here is the analysis:

---

### Title
Deposit Limit Reached for LST Asset Blocks `depositAssetForL1Vault()`, Leaving LSTs Idle in L1VaultV2 - (File: contracts/L1VaultV2.sol)

### Summary
When the per-asset deposit limit in `LRTConfig` is at or near capacity, `depositAssetForL1Vault()` in `L1VaultV2` will always revert with `MaximumDepositLimitReached`. Because the function unconditionally attempts to deposit the vault's **entire** LST balance, there is no partial-deposit fallback. Bridged LSTs accumulate in `L1VaultV2` and L2 users receive no rsETH until a `MANAGER` role holder raises the limit.

### Finding Description

**Call chain:**

`L1VaultV2.depositAssetForL1Vault(token)` reads the full token balance and calls `lrtDepositPool.depositAsset(token, tokenBalance, rsETHAmountToMint, "")`: [1](#0-0) 

`LRTDepositPool.depositAsset` calls `_beforeDeposit`, which calls `_checkIfDepositAmountExceedesCurrentLimit`: [2](#0-1) 

`_beforeDeposit` reverts with `MaximumDepositLimitReached` if the check returns `true`: [3](#0-2) 

The limit check for ERC-20 assets is:
```
totalAssetDeposits + amount > depositLimitByAsset[token]
``` [4](#0-3) 

`getTotalAssetDeposits` aggregates balances across the deposit pool, all NDCs, EigenLayer strategies, the converter, and the unstaking vault — so the limit can be reached organically as the protocol grows: [5](#0-4) 

The deposit limit is stored in `LRTConfig.depositLimitByAsset` and is updatable only by the `MANAGER` role: [6](#0-5) 

**Root cause:** `depositAssetForL1Vault` always passes `tokenBalance` (the full vault balance) to `depositAsset`. There is no mechanism to deposit a partial amount that fits within the remaining limit, and no mechanism to queue or retry. If even 1 wei of the deposit would exceed the cap, the entire call reverts. [7](#0-6) 

### Impact Explanation
LSTs bridged from L2 sit idle in `L1VaultV2`. L2 users who sent LSTs across the bridge receive no rsETH until a `MANAGER` role holder raises `depositLimitByAsset[token]`. No funds are lost, but the contract fails to deliver its promised conversion. This matches the scoped impact: **Low — Contract fails to deliver promised returns, but doesn't lose value.**

### Likelihood Explanation
No attacker action is required. The deposit limit is a normal protocol parameter that is reached organically as TVL grows. Any LST deposit that pushes `getTotalAssetDeposits(token) + tokenBalance` over the cap triggers the revert. This is a realistic steady-state condition for a growing protocol.

### Recommendation
In `depositAssetForL1Vault`, compute the remaining capacity via `lrtDepositPool.getAssetCurrentLimit(token)` and deposit only `min(tokenBalance, remainingLimit)` rather than the full balance. Alternatively, catch the revert and emit an event so the manager is alerted. The `getAssetCurrentLimit` view is already available: [8](#0-7) 

### Proof of Concept
1. Fork mainnet (or a local fork with the deployed contracts).
2. Fill the LST deposit limit: call `lrtDepositPool.depositAsset(token, remainingLimit, ...)` until `getAssetCurrentLimit(token) == 0`.
3. Bridge LSTs from L2 so that `L1VaultV2` holds a non-zero `tokenBalance`.
4. Call `L1VaultV2.depositAssetForL1Vault(token)` as `MANAGER_ROLE`.
5. Assert the call reverts with `MaximumDepositLimitReached`.
6. Confirm LSTs remain in `L1VaultV2` and no rsETH was minted.

### Citations

**File:** contracts/L1VaultV2.sol (L240-256)
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

**File:** contracts/LRTDepositPool.sol (L402-409)
```text
    function getAssetCurrentLimit(address asset) public view override returns (uint256) {
        uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
        if (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)) {
            return 0;
        }

        return lrtConfig.depositLimitByAsset(asset) - totalAssetDeposits;
    }
```

**File:** contracts/LRTDepositPool.sol (L661-663)
```text
        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }
```

**File:** contracts/LRTDepositPool.sol (L676-682)
```text
    function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
        uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
        if (asset == LRTConstants.ETH_TOKEN) {
            return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
        }
        return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
    }
```

**File:** contracts/LRTConfig.sol (L123-133)
```text
    function updateAssetDepositLimit(
        address asset,
        uint256 depositLimit
    )
        external
        onlyRole(LRTConstants.MANAGER)
        onlySupportedAsset(asset)
    {
        depositLimitByAsset[asset] = depositLimit;
        emit AssetDepositLimitUpdate(asset, depositLimit);
    }
```
