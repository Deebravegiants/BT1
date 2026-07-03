### Title
ETH Deposit Limit Bypass via Missing `amount` in `_checkIfDepositAmountExceedesCurrentLimit()` - (File: contracts/LRTDepositPool.sol)

---

### Summary

The `_checkIfDepositAmountExceedesCurrentLimit()` function in `LRTDepositPool.sol` applies an asymmetric check for ETH vs. LST assets. The ETH branch omits the incoming deposit `amount` from the comparison, allowing any user to deposit an arbitrarily large amount of ETH in a single transaction even when the configured `depositLimitByAsset` cap is nearly reached.

---

### Finding Description

The function at lines 676–682 reads:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← missing + amount
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← correct for LSTs
}
```

For LST assets the check correctly asks: *"would this deposit push the total over the limit?"* — `totalAssetDeposits + amount > limit`.

For ETH the check only asks: *"does the current total already exceed the limit?"* — `totalAssetDeposits > limit`. The incoming `amount` is never added. This means:

- If `totalAssetDeposits = 99 ETH` and `depositLimit = 100 ETH`, the check returns `false` regardless of whether `amount` is `1 ETH` or `1 000 000 ETH`.
- The deposit proceeds, minting rsETH for the full `amount`.

This is structurally identical to the reported analog: one code path (`depositAsset` / LST) has the guard, the parallel path (`depositETH` / ETH) is missing it. [1](#0-0) 

The caller entry point is the public `depositETH()` function, which is reachable by any unprivileged user: [2](#0-1) 

The limit itself is enforced via `_beforeDeposit`, which calls `_checkIfDepositAmountExceedesCurrentLimit`: [3](#0-2) 

---

### Impact Explanation

The `depositLimitByAsset` cap is a protocol-level risk management control. With the broken ETH check, a single depositor can push total ETH holdings arbitrarily beyond the configured limit in one transaction, causing the protocol to mint rsETH for amounts it was never designed to accept. The protocol fails to deliver its promised deposit cap for ETH.

**Impact: Low — Contract fails to deliver promised returns, but doesn't lose value.**

---

### Likelihood Explanation

Any unprivileged ETH depositor can trigger this. No special role, timing, or front-running is required. The attacker simply calls `depositETH()` with a large `msg.value` while `totalAssetDeposits < depositLimit`. Likelihood is **High**.

---

### Recommendation

Add `+ amount` to the ETH branch to match the LST branch:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

---

### Proof of Concept

1. Admin sets `depositLimitByAsset(ETH_TOKEN) = 100 ether` in `LRTConfig`.
2. Current `getTotalAssetDeposits(ETH_TOKEN)` returns `99 ether`.
3. Attacker calls `depositETH{value: 10_000 ether}(0, "")`.
4. Inside `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, 10_000 ether)`:
   - `totalAssetDeposits = 99 ether`
   - Check: `99 ether > 100 ether` → `false` → deposit is **not** blocked.
5. `_mintRsETH` mints rsETH for the full `10_000 ether`.
6. Total ETH in protocol is now `10_099 ether` — 100× the intended cap — with no revert. [1](#0-0) [4](#0-3)

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

**File:** contracts/LRTDepositPool.sol (L686-690)
```text
    function _mintRsETH(uint256 rsethAmountToMint) private {
        address rsethToken = lrtConfig.rsETH();
        // mint rseth for user
        IRSETH(rsethToken).mint(msg.sender, rsethAmountToMint);
    }
```
