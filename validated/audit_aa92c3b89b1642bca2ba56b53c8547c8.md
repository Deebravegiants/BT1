### Title
Fee-on-Transfer Token Deposits Cause rsETH Over-Minting Without Balance Validation - (File: contracts/LRTDepositPool.sol)

### Summary
`LRTDepositPool.depositAsset` mints rsETH based on the caller-supplied `depositAmount` parameter without verifying the contract's actual token balance increase after `safeTransferFrom`. If a fee-on-transfer LST is ever added as a supported asset, every deposit mints more rsETH than the protocol actually receives in backing collateral, progressively inflating the rsETH supply and driving the protocol toward insolvency.

### Finding Description
In `LRTDepositPool.depositAsset`, the amount of rsETH to mint is computed from the nominal `depositAmount` argument before the transfer executes:

```solidity
uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);
// interactions
IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
_mintRsETH(rsethAmountToMint);
``` [1](#0-0) 

`_beforeDeposit` calls `getRsETHAmountToMint(asset, depositAmount)`, which computes:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [2](#0-1) 

The contract never snapshots its balance before the transfer and never verifies that the balance increased by exactly `depositAmount` after it. For a fee-on-transfer token with a fee rate `f`, the contract receives `depositAmount * (1 - f)` but mints rsETH for the full `depositAmount`. The same structural gap exists across the L2 pool family:

- `RSETHPoolV3.deposit(address token, ...)` — mints wrsETH from nominal `amount` [3](#0-2) 

- `AGETHPoolV3.deposit(address token, ...)` — mints agETH from nominal `amount` [4](#0-3) 

- `RSETHPoolNoWrapper.deposit(address token, ...)` — transfers rsETH out based on nominal `amount` [5](#0-4) 

- `RsETHTokenWrapper._deposit` — mints wrsETH 1:1 with nominal `_amount` [6](#0-5) 

- `AGETHTokenWrapper._deposit` — mints agETH 1:1 with nominal `_amount` [7](#0-6) 

Notably, `KernelDepositPool.notifyRewardAmount` already applies the correct before/after balance pattern for reward tokens, demonstrating the developers are aware of the technique but did not apply it to deposit paths:

```solidity
uint256 balanceBefore = rewardsToken.balanceOf(address(this));
rewardsToken.safeTransferFrom(msg.sender, address(this), _amount);
uint256 balanceAfter = rewardsToken.balanceOf(address(this));
uint256 receivedAmount = balanceAfter - balanceBefore;
``` [8](#0-7) 

This inconsistency confirms the pattern is known and intentionally applied in one place but omitted in all deposit entry points.

### Impact Explanation
Every deposit with a fee-on-transfer LST mints rsETH in excess of the actual collateral received. Over time the rsETH total supply diverges from the real asset backing tracked by `getTotalAssetDeposits`, causing `rsETHPrice()` to be overstated. Later depositors receive fewer rsETH per unit of asset (dilution), and when withdrawers attempt to redeem rsETH for underlying assets the pool is short of collateral — a classic protocol insolvency. The impact is **Critical: protocol insolvency**.

### Likelihood Explanation
The `onlySupportedERC20Token` modifier restricts deposits to assets whitelisted by the admin via `LRTConfig`. Current mainnet LSTs (stETH, cbETH, rETH) are not fee-on-transfer. However, the protocol has an active expansion roadmap and has already added multiple new assets across L1 and L2 pools. Any future LST or bridged token that carries a transfer fee — added without the team auditing its transfer mechanics — immediately activates the vulnerability for every subsequent depositor. Likelihood is **Low** given current assets, but the missing guard creates a latent systemic risk that grows with each new asset listing.

### Recommendation
Apply the balance-before/after pattern consistently in every deposit path, mirroring what `KernelDepositPool.notifyRewardAmount` already does:

```solidity
function depositAsset(
    address asset,
    uint256 depositAmount,
    uint256 minRSETHAmountExpected,
    string calldata referralId
) external nonReentrant whenNotPaused onlySupportedERC20Token(asset) {
    uint256 balanceBefore = IERC20(asset).balanceOf(address(this));
    IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
    uint256 actualReceived = IERC20(asset).balanceOf(address(this)) - balanceBefore;

    // Use actualReceived, not depositAmount, for rsETH minting
    uint256 rsethAmountToMint = _beforeDeposit(asset, actualReceived, minRSETHAmountExpected);
    _mintRsETH(rsethAmountToMint);

    emit AssetDeposit(msg.sender, asset, actualReceived, rsethAmountToMint, referralId);
}
```

Apply the same fix to `RSETHPoolV3.deposit`, `AGETHPoolV3.deposit`, `RSETHPoolNoWrapper.deposit`, `RsETHTokenWrapper._deposit`, and `AGETHTokenWrapper._deposit`.

### Proof of Concept
1. Admin adds a fee-on-transfer LST (e.g., 1% fee) as a supported asset via `LRTConfig.addNewSupportedAsset`.
2. Alice calls `LRTDepositPool.depositAsset(feeToken, 100e18, 0, "")`.
3. `_beforeDeposit` computes `rsethAmountToMint` using `depositAmount = 100e18`.
4. `safeTransferFrom` executes; the contract receives only `99e18` (1% fee deducted).
5. `_mintRsETH(rsethAmountToMint)` mints rsETH calculated for `100e18`, not `99e18`.
6. Repeat across many depositors: rsETH supply inflates by 1% per deposit relative to actual collateral.
7. `rsETHPrice()` (computed from `getTotalAssetDeposits`) is now overstated; withdrawers who redeem rsETH for underlying assets find the pool short of collateral — permanent insolvency.

### Citations

**File:** contracts/LRTDepositPool.sol (L111-115)
```text
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L284-291)
```text
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

```

**File:** contracts/agETH/AGETHPoolV3.sol (L145-152)
```text
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 agETHAmount, uint256 fee) = viewSwapAgETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        agETH.mint(msg.sender, agETHAmount);

```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L262-269)
```text
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        rsETH.safeTransfer(msg.sender, rsETHAmount);

```

**File:** contracts/L2/RsETHTokenWrapper.sol (L134-140)
```text
    function _deposit(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);

        _mint(_to, _amount);
        emit Deposit(_asset, msg.sender, _to, _amount);
```

**File:** contracts/agETH/AGETHTokenWrapper.sol (L125-131)
```text
    function _deposit(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);

        _mint(_to, _amount);
        emit Deposit(_asset, _to, _amount);
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L573-577)
```text
        uint256 balanceBefore = rewardsToken.balanceOf(address(this));
        rewardsToken.safeTransferFrom(msg.sender, address(this), _amount);
        uint256 balanceAfter = rewardsToken.balanceOf(address(this));
        // Calculate the actual amount of tokens received in case of a transfer fee (tax)
        uint256 receivedAmount = balanceAfter - balanceBefore;
```
