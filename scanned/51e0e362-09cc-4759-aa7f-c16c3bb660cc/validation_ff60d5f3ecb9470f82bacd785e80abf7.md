The vulnerability is real and traceable. Let me confirm the exact code flow before writing the finding.

The `depositAsset()` function in `LRTDepositPool.sol` has a clear fee-on-transfer accounting flaw:

1. **Line 111**: `rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected)` — calls `getRsETHAmountToMint(asset, depositAmount)` using the caller-supplied `depositAmount` *before* any transfer occurs.
2. **Line 114**: `IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount)` — if the token deducts a fee, only `depositAmount - fee` arrives.
3. **Line 115**: `_mintRsETH(rsethAmountToMint)` — mints based on the full pre-transfer `depositAmount`.

There is no before/after balance check. The minted rsETH is permanently backed by fewer assets than accounted for.

---

### Title
Fee-on-Transfer LST Causes rsETH Over-Minting in `depositAsset()` - (File: contracts/LRTDepositPool.sol)

### Summary
`depositAsset()` calculates `rsethAmountToMint` from the caller-supplied `depositAmount` before executing the ERC20 transfer. For any whitelisted LST that deducts a transfer fee, the pool receives fewer tokens than the amount used to compute the mint, permanently over-minting rsETH relative to actual collateral.

### Finding Description
In `depositAsset()`, `_beforeDeposit()` is called first to compute `rsethAmountToMint` via `getRsETHAmountToMint(asset, depositAmount)`:

```solidity
// contracts/LRTDepositPool.sol line 111
uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);
```

`getRsETHAmountToMint` computes:

```solidity
// line 520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

where `amount` is the raw `depositAmount` argument. The transfer then occurs:

```solidity
// line 114
IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
```

For a fee-on-transfer token with fee rate `f`, the pool receives `depositAmount * (1 - f)` tokens, but mints rsETH for `depositAmount`. The deficit is never reconciled. No before/after balance snapshot is taken anywhere in the function. [1](#0-0) [2](#0-1) [3](#0-2) 

### Impact Explanation
Every deposit with a fee-on-transfer LST mints more rsETH than the collateral received justifies. `getTotalAssetDeposits()` reads live `balanceOf()` values, so the oracle-computed `rsETHPrice` will reflect the shortfall on the next price update, permanently diluting the exchange rate for all existing rsETH holders. No funds are directly stolen, but depositors receive rsETH that is not fully backed — matching the **Low** scope: *contract fails to deliver promised returns, but doesn't lose value*. [4](#0-3) 

### Likelihood Explanation
The `onlySupportedERC20Token` modifier gates deposits to admin-whitelisted assets. Current mainnet LSTs (stETH, rETH, cbETH, swETH) do not charge transfer fees, so the bug is dormant today. However, the protocol's asset list is extensible by the LRT admin with no code-level guard against fee-on-transfer tokens. Any future addition of such an LST (e.g., a rebasing token with a fee mechanism) immediately activates the vulnerability for every subsequent deposit. Likelihood is **Low** given current assets, but the structural absence of a balance-check pattern makes it a latent risk. [5](#0-4) 

### Recommendation
Replace the pre-transfer amount with a post-transfer balance delta:

```solidity
function depositAsset(...) external nonReentrant whenNotPaused onlySupportedERC20Token(asset) {
    uint256 balanceBefore = IERC20(asset).balanceOf(address(this));
    IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
    uint256 actualReceived = IERC20(asset).balanceOf(address(this)) - balanceBefore;

    uint256 rsethAmountToMint = _beforeDeposit(asset, actualReceived, minRSETHAmountExpected);
    _mintRsETH(rsethAmountToMint);

    emit AssetDeposit(msg.sender, asset, actualReceived, rsethAmountToMint, referralId);
}
```

This ensures rsETH is always minted against tokens actually held by the pool.

### Proof of Concept
1. Deploy a mock ERC20 LST with a 1% transfer fee (fee deducted from recipient on every `transferFrom`).
2. Whitelist the mock token via `LRTConfig` (admin action, not part of the exploit itself).
3. Call `depositAsset(mockToken, 1e18, 0, "")` from an unprivileged account.
4. Pool receives `0.99e18` tokens; rsETH minted corresponds to `1e18` tokens.
5. Assert: `rsETHPrice * rsETH.totalSupply() > actual pool collateral value` — the invariant is broken.
6. Repeat N times; each deposit widens the gap, permanently reducing the rsETH/ETH exchange rate for all holders.

### Citations

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

**File:** contracts/LRTDepositPool.sol (L506-521)
```text
    function getRsETHAmountToMint(
        address asset,
        uint256 amount
    )
        public
        view
        override
        returns (uint256 rsethAmountToMint)
    {
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTDepositPool.sol (L648-670)
```text
    function _beforeDeposit(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected
    )
        private
        view
        returns (uint256 rsethAmountToMint)
    {
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
    }
```
