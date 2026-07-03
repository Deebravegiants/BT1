### Title
ETH Deposit Limit Bypass via Incomplete Amount Check in `_checkIfDepositAmountExceedesCurrentLimit` - (File: contracts/LRTDepositPool.sol)

### Summary
`LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit` applies an asymmetric check: for ERC20 LST assets it correctly tests `totalAssetDeposits + amount > limit`, but for native ETH it only tests `totalAssetDeposits > limit`, omitting the incoming deposit amount. Any depositor can therefore push total ETH deposits arbitrarily above the configured `depositLimitByAsset[ETH_TOKEN]` cap in a single `depositETH` call.

### Finding Description
The deposit-limit guard lives in a single private helper:

```solidity
// contracts/LRTDepositPool.sol
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← amount ignored
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← correct for ERC20
}
```

For ERC20 LSTs the prospective deposit is included in the comparison, so a deposit that would breach the cap is rejected. For ETH the comparison only checks whether the current total already exceeds the limit; the incoming `amount` is never added. Consequently, as long as `totalAssetDeposits ≤ depositLimit` at the moment of the call, any `amount` of ETH passes the guard and is accepted, even if it would push the total far above the limit.

The vulnerable entry point is `depositETH`, which is public and callable by any user:

```solidity
function depositETH(uint256 minRSETHAmountExpected, string calldata referralId)
    external payable nonReentrant whenNotPaused onlySupportedAsset(LRTConstants.ETH_TOKEN)
{
    uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);
    _mintRsETH(rsethAmountToMint);
    ...
}
```

`_beforeDeposit` calls `_checkIfDepositAmountExceedesCurrentLimit`, which for ETH will return `false` (not exceeded) whenever `totalAssetDeposits ≤ limit`, regardless of `msg.value`.

### Impact Explanation
The `depositLimitByAsset` cap is the protocol's primary mechanism for controlling how much of each asset it accepts. Bypassing it for ETH allows unlimited rsETH to be minted against ETH deposits beyond the intended ceiling. This breaks the protocol's risk-management invariant: the protocol may accept more ETH than EigenLayer strategies can absorb, leaving excess ETH stranded in the deposit pool or NDCs with no downstream strategy, and minting rsETH that is not fully backed by restaked positions. This maps to **Low – contract fails to deliver promised returns** (the deposit cap promise is broken) with a path to **Medium – temporary freezing of funds** if the excess ETH cannot be forwarded to EigenLayer.

### Likelihood Explanation
The path is fully permissionless: any user who calls `depositETH` with `msg.value` large enough to exceed the remaining cap triggers the bug. No special role, front-running, or external dependency is required. The condition is reachable whenever the ETH deposit limit is set to a finite value and the pool is not paused.

### Recommendation
Include the deposit amount in the ETH branch of `_checkIfDepositAmountExceedesCurrentLimit`, matching the ERC20 logic:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

### Proof of Concept
1. Admin sets `depositLimitByAsset[ETH_TOKEN] = 1000 ether`.
2. Existing deposits bring `getTotalAssetDeposits(ETH_TOKEN)` to exactly `1000 ether`.
3. User calls `depositETH{value: 500 ether}(0, "")`.
4. `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, 500 ether)` evaluates `1000 ether > 1000 ether` → `false` → check passes.
5. `_mintRsETH` mints rsETH for 500 ETH; total ETH deposits are now `1500 ether`, 50 % above the cap.
6. For comparison, `depositAsset(stETH, 500 ether, ...)` at the same state evaluates `1000 ether + 500 ether > 1000 ether` → `true` → correctly reverts with `MaximumDepositLimitReached`. [1](#0-0) [2](#0-1) [3](#0-2)

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
