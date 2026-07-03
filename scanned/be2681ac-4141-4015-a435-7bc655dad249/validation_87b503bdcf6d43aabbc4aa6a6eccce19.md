### Title
ETH Deposit Limit Bypass Due to Missing Amount in Boundary Check - (`contracts/LRTDepositPool.sol`)

---

### Summary

`_checkIfDepositAmountExceedesCurrentLimit` in `LRTDepositPool` applies an inconsistent boundary check for ETH versus ERC20 assets. For ETH, the incoming deposit `amount` is omitted from the comparison, so the limit is only enforced after it has already been exceeded — not before. Any depositor can push the total ETH deposits above `depositLimitByAsset(ETH)` in a single call.

---

### Finding Description

In `LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit`:

```solidity
// contracts/LRTDepositPool.sol L676-L682
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← amount NOT included
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← amount included
}
```

For ERC20 assets the check is `totalAssetDeposits + amount > limit` — correct. For ETH the check is `totalAssetDeposits > limit` — the incoming `amount` is never added. This means:

- When `totalAssetDeposits == limit`, the function returns `false` (not exceeded), so `_beforeDeposit` does not revert.
- The depositor's ETH is accepted and rsETH is minted.
- After the call, `totalAssetDeposits` equals `limit + msg.value`, violating the configured cap.

The call path is fully public:

1. Attacker calls `depositETH{value: X}(...)` — `LRTDepositPool.sol` L76-L93
2. `_beforeDeposit` calls `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, X)` — L661
3. Check returns `false` even when `totalAssetDeposits + X > limit` — L679
4. `_mintRsETH` mints rsETH for the full `X` — L90

---

### Impact Explanation

The ETH deposit cap (`depositLimitByAsset`) is a protocol-level safety parameter. Bypassing it allows the protocol to accept and restake more ETH than intended, minting rsETH beyond the configured ceiling. This constitutes the contract failing to deliver its promised deposit-limit guarantee.

**Impact: Low — Contract fails to deliver promised returns (deposit limit not enforced for ETH).**

---

### Likelihood Explanation

Any unprivileged ETH depositor can trigger this in a single transaction whenever `totalAssetDeposits` is at or near the configured limit. No special role, front-running, or external dependency is required. Likelihood is **High** given the public entry point and zero preconditions beyond the limit being approached.

---

### Recommendation

Apply the same `+ amount` inclusion to the ETH branch:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

---

### Proof of Concept

Assume `depositLimitByAsset(ETH) = 1000 ether` and `totalAssetDeposits(ETH) = 1000 ether`.

1. Attacker calls `depositETH{value: 500 ether}(0, "")`.
2. `_checkIfDepositAmountExceedesCurrentLimit(ETH, 500 ether)` evaluates `1000 ether > 1000 ether` → `false`.
3. `_beforeDeposit` does not revert; rsETH is minted for 500 ETH.
4. `totalAssetDeposits(ETH)` is now `1500 ether`, 50% above the configured limit.

The ERC20 path would have evaluated `1000 + 500 > 1000` → `true` → revert, correctly blocking the deposit. [1](#0-0) [2](#0-1) [3](#0-2)

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
