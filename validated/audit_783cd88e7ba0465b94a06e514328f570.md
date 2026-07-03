### Title
ETH Deposit Limit Check Omits New Deposit Amount, Allowing Limit Bypass - (File: contracts/LRTDepositPool.sol)

---

### Summary

`_checkIfDepositAmountExceedesCurrentLimit` in `LRTDepositPool.sol` applies an asymmetric comparison for ETH versus ERC20 assets. The ETH branch omits the incoming deposit `amount` from the comparison, so the limit is never enforced against the deposit that is about to land. Any unprivileged depositor can push ETH holdings past the configured `depositLimitByAsset` cap.

---

### Finding Description

`_checkIfDepositAmountExceedesCurrentLimit` is the sole gate that enforces the per-asset deposit cap before minting rsETH:

```solidity
// contracts/LRTDepositPool.sol  lines 676-682
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← amount missing
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← correct
}
```

For every ERC20 LST the check is `totalAssetDeposits + amount > limit`, which correctly blocks a deposit that would breach the cap. For native ETH the check is `totalAssetDeposits > limit`, which only returns `true` when the cap is **already** exceeded. A deposit that would bring the total from `limit - 1 wei` to `limit + msg.value` passes the check and is accepted.

The correct ETH branch should mirror the ERC20 branch:

```solidity
return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
```

The wrong comparison is structurally identical to the reference report: a threshold check whose inequality is off by one logical step, causing the guard to fire in the wrong state.

---

### Impact Explanation

The `depositLimitByAsset` cap is the protocol's primary mechanism for bounding ETH exposure. With the broken check, any depositor can call `depositETH` and receive rsETH for ETH that exceeds the intended cap. The protocol mints rsETH backed by more ETH than governance approved, violating the promised deposit ceiling. This is a **Low** impact: the contract fails to deliver its promised deposit-limit guarantee, but no funds are directly stolen or frozen.

---

### Likelihood Explanation

The entry path is fully permissionless. `depositETH` is a public `payable` function with no role restriction. Any user who monitors on-chain state and sees `totalAssetDeposits` approaching `depositLimitByAsset(ETH_TOKEN)` can immediately exploit the gap. Likelihood is **High**.

---

### Recommendation

Replace the ETH branch with the same expression used for ERC20 tokens:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

The special-casing of `ETH_TOKEN` is unnecessary because `getTotalAssetDeposits` already handles ETH correctly via `getETHDistributionData`.

---

### Proof of Concept

1. Assume `depositLimitByAsset(ETH_TOKEN) = 100 ether` and `getTotalAssetDeposits(ETH_TOKEN) = 100 ether - 1 wei`.
2. Attacker calls `depositETH{value: 10 ether}(...)`.
3. `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, 10 ether)` evaluates `(100 ether - 1 wei) > 100 ether` → `false` → limit not exceeded.
4. `_beforeDeposit` does not revert; rsETH is minted for 10 ETH.
5. `getTotalAssetDeposits(ETH_TOKEN)` is now `110 ether - 1 wei`, exceeding the cap by ~10 ETH.

The ERC20 path for the same scenario would evaluate `(100 ether - 1 wei) + 10 ether > 100 ether` → `true` → deposit correctly rejected. [1](#0-0) [2](#0-1) [3](#0-2)

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
