The vulnerability is real. The code confirms the asymmetry exactly as described.

### Title
ETH deposit cap bypass due to missing `+ amount` in `_checkIfDepositAmountExceedesCurrentLimit` — (`contracts/LRTDepositPool.sol`)

---

### Summary

`_checkIfDepositAmountExceedesCurrentLimit` uses a strict greater-than check without adding the incoming `amount` for the ETH branch, while the ERC20 branch correctly includes `+ amount`. This allows any ETH deposit to succeed as long as `totalAssetDeposits <= depositLimit`, even when the deposit itself would push the total above the cap.

---

### Finding Description

In `_checkIfDepositAmountExceedesCurrentLimit`:

```solidity
// contracts/LRTDepositPool.sol L676-L682
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← missing + amount
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← correct
}
```

The ETH branch returns `true` (blocks) only when the total has **already** exceeded the limit. It never accounts for the incoming `amount`. The ERC20 branch correctly checks whether the deposit **would** push the total over the limit.

Concrete scenario:
- `depositLimitByAsset(ETH_TOKEN) = 1000 ether`
- `totalAssetDeposits(ETH_TOKEN) = 999 ether`
- Depositor calls `depositETH{value: 100 ether}(...)`
- ETH check: `999 > 1000` → `false` → deposit allowed
- After deposit: `totalAssetDeposits = 1099 ether`, exceeding the cap by 99 ether

This is also confirmed by the inconsistency with `getAssetCurrentLimit`: when `totalAssetDeposits == limit`, that function correctly returns `0` (no room left), yet `_checkIfDepositAmountExceedesCurrentLimit` returns `false` (not exceeded) for ETH, allowing the deposit. [1](#0-0) 

The call path is fully unprivileged:

`depositETH()` → `_beforeDeposit()` → `_checkIfDepositAmountExceedesCurrentLimit()` → `_mintRsETH()` [2](#0-1) [3](#0-2) 

---

### Impact Explanation

The ETH deposit cap is violated. The protocol enforces a per-asset TVL ceiling via `depositLimitByAsset`, but for ETH the ceiling is not enforced on the incoming deposit amount — only on the pre-deposit state. Any depositor can push ETH TVL above the configured cap.

The exchange rate is **not** diluted (the depositor sends real ETH backing the minted rsETH), so there is no fund loss. The impact is that the protocol fails to enforce its own deposit cap invariant. This matches **Low — Contract fails to deliver promised returns, but doesn't lose value**. [4](#0-3) 

---

### Likelihood Explanation

No special role or privilege is required. Any user can trigger this by calling `depositETH` with any nonzero `msg.value` when `totalAssetDeposits` is at or near the limit. The condition is reachable in normal protocol operation whenever the ETH cap is close to full.

---

### Recommendation

Change the ETH branch to mirror the ERC20 branch by including `+ amount`:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
``` [5](#0-4) 

---

### Proof of Concept

```solidity
// Pseudocode for a local fork/unit test
uint256 cap = lrtConfig.depositLimitByAsset(ETH_TOKEN);

// Bring total deposits to exactly the cap via prior deposits
// (or mock getTotalAssetDeposits to return cap)
assertEq(depositPool.getAssetCurrentLimit(ETH_TOKEN), 0); // correctly reports 0 room

// Now attempt an ETH deposit — should revert with MaximumDepositLimitReached
// but it succeeds:
depositPool.depositETH{value: 1 ether}(0, "");

// Total deposits now exceed cap
assertGt(depositPool.getTotalAssetDeposits(ETH_TOKEN), cap);
``` [1](#0-0)

### Citations

**File:** contracts/LRTDepositPool.sol (L76-92)
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
```

**File:** contracts/LRTDepositPool.sol (L402-409)
```text
    function getAssetCurrentLimit(address asset) public view override returns (uint256) {
        uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
        if (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)) {
            return 0;
        }

        return lrtConfig.depositLimitByAsset(asset) - totalAssetDeposits;
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
