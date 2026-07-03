### Title
ETH Deposit Limit Bypass via Missing Amount in `_checkIfDepositAmountExceedesCurrentLimit` - (File: contracts/LRTDepositPool.sol)

### Summary

The `_checkIfDepositAmountExceedesCurrentLimit()` function in `LRTDepositPool` applies an asymmetric check: for LST assets it correctly includes the incoming deposit amount in the comparison, but for ETH it omits the deposit amount entirely. Any unprivileged depositor can therefore bypass the ETH `depositLimitByAsset` cap in a single transaction.

### Finding Description

`_checkIfDepositAmountExceedesCurrentLimit` has two branches:

```solidity
// contracts/LRTDepositPool.sol  lines 676-682
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← amount NOT included
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← amount included
}
```

For every LST the check is `totalAssetDeposits + amount > limit`, which correctly blocks a deposit that would push the total over the cap. For ETH the check is only `totalAssetDeposits > limit`, which is `false` whenever the current total has not yet exceeded the limit — regardless of how large `amount` is. The function therefore returns `false` (i.e., "not exceeded") and the deposit proceeds, even when `totalAssetDeposits + msg.value` would far exceed `depositLimitByAsset[ETH_TOKEN]`.

The call chain is:

`depositETH()` → `_beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, …)` → `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, msg.value)` [1](#0-0) [2](#0-1) 

### Impact Explanation

The `depositLimitByAsset` cap is the protocol's primary risk-management invariant for each supported asset. Bypassing it for ETH allows an attacker (or any ordinary depositor) to push the total ETH held by the protocol arbitrarily above the configured limit in a single call. This breaks the protocol's stated deposit cap invariant and causes the contract to fail to deliver its promised risk-bounded behaviour. Impact classification: **Low — contract fails to deliver promised returns**. [3](#0-2) [4](#0-3) 

### Likelihood Explanation

The entry point `depositETH()` is a public, permissionless, non-paused function. No special role, prior state, or front-running is required. Any depositor who sends ETH while `totalAssetDeposits < depositLimitByAsset[ETH_TOKEN]` can exceed the cap in one transaction. Likelihood is **High**. [2](#0-1) 

### Recommendation

Apply the same `totalAssetDeposits + amount` pattern to the ETH branch:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
``` [5](#0-4) 

### Proof of Concept

1. Admin sets `depositLimitByAsset[ETH_TOKEN] = 100 ether`.
2. Current `getTotalAssetDeposits(ETH_TOKEN)` returns `99 ether`.
3. Attacker calls `depositETH{value: 500 ether}(0, "")`.
4. `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, 500 ether)` evaluates `99 ether > 100 ether` → `false` → no revert.
5. `_mintRsETH` mints rsETH for 500 ETH; `getTotalAssetDeposits(ETH_TOKEN)` is now `599 ether`, nearly 6× the intended cap.
6. The deposit limit invariant is permanently broken for this epoch; subsequent honest depositors are blocked while the attacker's over-limit position is already accepted. [1](#0-0) [6](#0-5)

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

**File:** contracts/LRTConfig.sol (L23-23)
```text
    mapping(address token => uint256 amount) public depositLimitByAsset;
```
