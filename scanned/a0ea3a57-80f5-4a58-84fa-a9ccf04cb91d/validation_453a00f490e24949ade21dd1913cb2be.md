### Title
Incorrect Deposit Limit Check for ETH Omits New Deposit Amount, Allowing Limit Bypass - (File: contracts/LRTDepositPool.sol)

### Summary
`_checkIfDepositAmountExceedesCurrentLimit()` in `LRTDepositPool.sol` applies an asymmetric check: for ERC20 assets it correctly includes the incoming deposit amount (`totalAssetDeposits + amount > depositLimit`), but for ETH it omits the new amount entirely (`totalAssetDeposits > depositLimit`). This mirrors the external report's class of **incorrect return value in a check function** — the function returns `false` (no revert) for ETH deposits that would push total deposits past the configured limit.

### Finding Description
In `LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit()`:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← missing `+ amount`
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
``` [1](#0-0) 

For ETH the function only checks whether the limit is **already exceeded** before the deposit, not whether the incoming deposit **would** exceed it. For every ERC20 asset the incoming `amount` is correctly included in the comparison.

This function is the sole deposit-limit gate called inside `_beforeDeposit`, which is invoked by the public `depositETH()` entry point:

```solidity
if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
    revert MaximumDepositLimitReached();
}
``` [2](#0-1) 

### Impact Explanation
Any depositor can push the ETH total deposits above `depositLimitByAsset[ETH_TOKEN]`. The deposit limit is the protocol's primary risk-management cap on ETH exposure routed into EigenLayer strategies. Bypassing it means the protocol silently accepts more ETH than governance intended, violating the invariant that `getTotalAssetDeposits(ETH) ≤ depositLimitByAsset[ETH]`.

**Impact: Low** — Contract fails to deliver its promised deposit-cap guarantee for ETH; no direct fund loss or freeze occurs, but the risk-management invariant is broken for every ETH deposit made while `totalAssetDeposits == depositLimit`.

### Likelihood Explanation
The condition is trivially reachable: any unprivileged depositor calling `depositETH()` when `getTotalAssetDeposits(ETH_TOKEN) == depositLimitByAsset[ETH_TOKEN]` will bypass the cap. No special role, timing, or oracle manipulation is required.

### Recommendation
Add the incoming `amount` to the ETH branch, matching the ERC20 branch:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
``` [3](#0-2) 

### Proof of Concept
1. Admin sets `depositLimitByAsset[ETH_TOKEN] = 100 ether`.
2. Protocol accumulates exactly `100 ether` in ETH deposits (`getTotalAssetDeposits(ETH_TOKEN) == 100 ether`).
3. `getAssetCurrentLimit(ETH_TOKEN)` returns `0` — signalling no remaining capacity.
4. Attacker calls `depositETH{value: 50 ether}(0, "")`.
5. Inside `_beforeDeposit`, `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, 50 ether)` evaluates `100 ether > 100 ether` → `false` → no revert.
6. 50 rsETH is minted; `getTotalAssetDeposits(ETH_TOKEN)` is now `150 ether`, 50% above the configured cap.
7. The same call with any ERC20 at the same state would correctly revert with `MaximumDepositLimitReached`. [4](#0-3) [5](#0-4)

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
