### Title
Lax ETH Deposit Limit Check Allows Deposits Beyond Protocol Cap - (File: contracts/LRTDepositPool.sol)

### Summary
`LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit` applies an asymmetric validation: for ERC-20 assets it correctly checks `totalAssetDeposits + amount > limit`, but for ETH it only checks `totalAssetDeposits > limit`, omitting the incoming deposit amount. Any depositor can push the ETH total above the configured cap in a single call.

### Finding Description
`_checkIfDepositAmountExceedesCurrentLimit` contains a branch split on asset type:

```solidity
// contracts/LRTDepositPool.sol L676-L682
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← amount ignored
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← correct
}
```

For ETH the function returns `false` (i.e., "not exceeded") whenever `totalAssetDeposits ≤ limit`, regardless of how large `amount` is. The check is called inside `_beforeDeposit`, which is the sole guard invoked by `depositETH`:

```solidity
// contracts/LRTDepositPool.sol L661-L663
if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
    revert MaximumDepositLimitReached();
}
```

Because `amount` is never added to `totalAssetDeposits` before the comparison, a depositor whose transaction would push the running total from `limit - ε` to `limit + X` passes the check and receives freshly minted rsETH. The ERC-20 path (`depositAsset`) performs the correct inclusive check and is not affected.

### Impact Explanation
The deposit limit is the protocol's primary mechanism for capping ETH exposure (e.g., to match EigenLayer restaking capacity or risk parameters). Bypassing it allows unlimited ETH to be deposited and rsETH to be minted beyond the intended ceiling. Excess ETH that cannot be restaked in EigenLayer sits idle in the deposit pool or NDCs without generating yield, meaning rsETH holders receive diluted returns on that portion. No direct theft occurs, but the contract fails to deliver the promised deposit-cap guarantee.

**Impact: Low — Contract fails to deliver promised returns, but doesn't lose value.**

### Likelihood Explanation
The condition is reachable by any unprivileged depositor calling `depositETH` with `msg.value > 0` at any time the ETH total is at or below the configured limit. No special role, timing, or front-running is required. The gap between the lax check and the correct check is always present and grows with deposit size.

**Likelihood: High.**

### Recommendation
Apply the same inclusive check used for ERC-20 assets to the ETH branch:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

This mirrors the ERC-20 path and closes the asymmetry.

### Proof of Concept
1. Admin sets `depositLimitByAsset(ETH_TOKEN) = 1000 ether`.
2. Current `getTotalAssetDeposits(ETH_TOKEN)` returns `999 ether`.
3. Depositor calls `depositETH{value: 500 ether}(0, "")`.
4. `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, 500 ether)` evaluates `999 ether > 1000 ether` → `false` → no revert.
5. `_mintRsETH` mints rsETH for 500 ETH; total ETH in protocol becomes `1499 ether`, 49.9 % above the cap.
6. The same depositor (or any other) can repeat until EigenLayer capacity or other external constraints are hit. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/LRTDepositPool.sol (L76-93)
```text
    function depositETH(
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        payable
        nonReentrant
        whenNotPaused
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
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
