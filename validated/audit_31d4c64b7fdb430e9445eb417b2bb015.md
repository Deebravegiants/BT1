### Title
Missing `amount` in ETH Deposit Limit Check Allows Deposit Cap Bypass — (File: contracts/LRTDepositPool.sol)

---

### Summary

`LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit` applies an inconsistent comparison for ETH versus ERC-20 assets: the ETH branch omits the incoming deposit `amount` from the limit comparison, while the ERC-20 branch correctly includes it. Any unprivileged depositor can therefore bypass the ETH deposit cap entirely in a single transaction.

---

### Finding Description

**Root cause — missing constraint on the deposit amount for ETH:** [1](#0-0) 

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← amount missing
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← correct
}
```

For ETH the guard is `totalAssetDeposits > limit`, which is `true` only when the cap is **already** exceeded. It never tests whether the *incoming* deposit would push the total over the cap. For every ERC-20 asset the guard is `totalAssetDeposits + amount > limit`, which is the correct forward-looking check.

**Caller path:** [2](#0-1) 

`depositETH` → `_beforeDeposit` → `_checkIfDepositAmountExceedesCurrentLimit`. If the function returns `false` the deposit is accepted unconditionally. [3](#0-2) 

**Exploit flow:**

1. Observe `totalAssetDeposits(ETH) = X` where `X ≤ depositLimit`.
2. Call `depositETH{value: Y}("")` with arbitrarily large `Y`.
3. The check evaluates `X > depositLimit` → `false` → deposit is not blocked.
4. `_mintRsETH` mints rsETH proportional to `Y` at the current oracle rate.
5. After the call `totalAssetDeposits(ETH) = X + Y`, which may be orders of magnitude above the cap.

---

### Impact Explanation

The ETH deposit cap is a risk-management control that bounds the protocol's exposure to a single asset. Bypassing it in one transaction allows a depositor to push the protocol's ETH holdings arbitrarily above the intended ceiling. The depositor receives rsETH at the prevailing rate (no direct theft), but the protocol's risk posture is violated: restaking capacity may be exceeded, the rsETH price calculation absorbs the full inflated TVL, and subsequent depositors interact with a protocol that is operating outside its designed parameters. This maps to **Low — contract fails to deliver its promised invariant (the deposit cap) without losing value**.

---

### Likelihood Explanation

The entry point is the public, permissionless `depositETH` function. No role, no special state, and no front-running is required. Any depositor with sufficient ETH can trigger this in a single transaction whenever `totalAssetDeposits(ETH) ≤ depositLimit`.

---

### Recommendation

Apply the same forward-looking check to ETH that is already applied to ERC-20 assets:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
``` [1](#0-0) 

---

### Proof of Concept

```
depositLimit(ETH)      = 100 ETH
totalAssetDeposits(ETH) = 50 ETH   (before attack)

Attacker calls: depositETH{value: 10_000 ETH}("")

_checkIfDepositAmountExceedesCurrentLimit(ETH, 10_000 ETH):
  totalAssetDeposits = 50 ETH
  return (50 > 100)  →  false   ← cap check passes, amount ignored

_mintRsETH mints rsETH for 10_000 ETH at current rate.

totalAssetDeposits(ETH) after = 10_050 ETH  (100× over the cap)
```

The deposit limit is bypassed because the `amount` parameter is never included in the ETH branch of the guard, mirroring the class of missing-constraint bugs where a value that must be bounded is left unchecked, allowing an attacker to operate outside the protocol's intended safety envelope.

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
