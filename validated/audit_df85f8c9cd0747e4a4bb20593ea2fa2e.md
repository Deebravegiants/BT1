### Title
ETH Deposit Limit Bypass Due to Missing Deposit Amount in Limit Check - (File: contracts/LRTDepositPool.sol)

### Summary
`_checkIfDepositAmountExceedesCurrentLimit` in `LRTDepositPool.sol` omits the incoming deposit amount (`amount`) from the limit comparison when the asset is ETH, while correctly including it for all other assets. This allows any depositor to push total ETH deposits beyond the configured cap.

### Finding Description
In `_checkIfDepositAmountExceedesCurrentLimit`, the function branches on whether the asset is `ETH_TOKEN`:

```solidity
// contracts/LRTDepositPool.sol lines 676-682
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← amount NOT included
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← amount included
}
```

For every non-ETH LST the check is `totalAssetDeposits + amount > limit`, which correctly blocks a deposit that would push the total over the cap. For ETH the check is only `totalAssetDeposits > limit`, which only blocks deposits when the cap is **already exceeded**. Any deposit that would bring the total from at-or-below the cap to above it passes unchecked.

This is structurally identical to the reported class: a guard that should always evaluate the incoming quantity is placed inside a conditional branch where it is silently dropped for one code path.

### Impact Explanation
Any unprivileged depositor can call `depositETH()` and receive freshly minted rsETH even when the ETH deposit limit has been reached. The protocol's risk-management cap for ETH is rendered ineffective. The protocol mints rsETH backed by more ETH than the admin intended to accept, violating the invariant enforced for every other supported asset.

**Impact**: Low — Contract fails to deliver promised returns (deposit cap enforcement) but deposited ETH is not lost; rsETH is minted at the correct exchange rate.

### Likelihood Explanation
The entry point is the public, permissionless `depositETH()` function. No special role, front-running, or external dependency is required. Any depositor who observes that `getTotalAssetDeposits(ETH_TOKEN) >= depositLimitByAsset(ETH_TOKEN)` can immediately exploit this by sending any non-zero ETH amount.

### Recommendation
Include the deposit amount in the ETH branch, matching the non-ETH logic:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

### Proof of Concept
1. Admin sets `depositLimitByAsset[ETH_TOKEN] = 1000 ether`.
2. Legitimate deposits bring `getTotalAssetDeposits(ETH_TOKEN)` to exactly `1000 ether`.
3. Attacker calls `depositETH{value: 500 ether}(0, "")`.
4. `_beforeDeposit` calls `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, 500 ether)`.
5. Inside the function: `totalAssetDeposits = 1000 ether`; the ETH branch evaluates `1000 ether > 1000 ether` → `false`.
6. The revert is never triggered; `_mintRsETH` executes and the attacker receives rsETH.
7. `getTotalAssetDeposits(ETH_TOKEN)` is now `1500 ether`, 50 % above the configured cap. [1](#0-0) [2](#0-1) [3](#0-2)

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

**File:** contracts/LRTDepositPool.sol (L648-663)
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
