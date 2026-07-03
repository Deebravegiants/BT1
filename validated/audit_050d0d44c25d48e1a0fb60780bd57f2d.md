### Title
ETH Deposit Limit Check Omits Incoming Amount, Allowing Cap Bypass - (File: contracts/LRTDepositPool.sol)

### Summary
In `LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit`, the ETH branch of the deposit-limit check omits the incoming deposit `amount` from the comparison. The ERC-20 branch correctly includes `amount`, but the ETH branch only tests whether the *current* total already exceeds the limit. This means any depositor can push the ETH total above `depositLimitByAsset[ETH_TOKEN]` in a single call, permanently bypassing the cap.

### Finding Description
`_checkIfDepositAmountExceedesCurrentLimit` (lines 676–682) has two return paths:

```solidity
// ETH path — amount is NOT included
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
}
// ERC-20 path — amount IS included (correct)
return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
```

For ETH the function returns `true` (blocked) only when `totalAssetDeposits > depositLimit`. It returns `false` (allowed) whenever `totalAssetDeposits <= depositLimit`, regardless of how large `amount` is. Concretely:

- If `totalAssetDeposits == depositLimit`, the check returns `false`, so the deposit proceeds and the new total becomes `depositLimit + amount`.
- If `totalAssetDeposits < depositLimit` but `totalAssetDeposits + amount > depositLimit`, the check still returns `false`, allowing the overshoot.

The ERC-20 path (`totalAssetDeposits + amount > depositLimit`) correctly blocks both cases.

### Impact Explanation
The ETH deposit cap (`depositLimitByAsset[ETH_TOKEN]`) is a protocol-level safety ceiling. Because the incoming `amount` is excluded from the ETH comparison, any unprivileged depositor can exceed that ceiling in a single `depositETH` call. The protocol mints rsETH for the excess ETH and the cap is permanently overshot. No funds are stolen, but the protocol delivers more rsETH than the deposit limit was designed to permit.

**Impact: Low — Contract fails to deliver promised returns (deposit limit not enforced for ETH).**

### Likelihood Explanation
The entry point is `depositETH`, a public payable function callable by any user. No special role, front-running, or external dependency is required. The condition is met naturally whenever the ETH pool approaches its configured limit, which is a normal operational state.

### Recommendation
Add `amount` to the ETH comparison, matching the ERC-20 path:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

### Proof of Concept
1. Admin sets `depositLimitByAsset[ETH_TOKEN] = 1000 ether`.
2. Through normal deposits, `getTotalAssetDeposits(ETH_TOKEN)` reaches exactly `1000 ether`.
3. Attacker calls `depositETH{value: 500 ether}(0, "")`.
4. `_checkIfDepositAmountExceedesCurrentLimit` evaluates `1000 ether > 1000 ether` → `false` → no revert.
5. `_mintRsETH` mints rsETH for 500 ETH; total ETH in protocol is now `1500 ether`, 50 % above the intended cap.
6. The ERC-20 equivalent call with the same numbers would have evaluated `1000 + 500 > 1000` → `true` → reverted. [1](#0-0) [2](#0-1) [3](#0-2)

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
