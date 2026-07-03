Looking at the vulnerability class — **insufficient validation where a minimum/limit check can be bypassed** — I need to find an analog in LRT-rsETH where a validation check fails to enforce the intended constraint, allowing an unprivileged caller to exceed a protocol-enforced limit.

The key finding is in `LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit()`: [1](#0-0) 

For ETH the check is `totalAssetDeposits > depositLimit` (without adding `amount`), while for LSTs it correctly uses `totalAssetDeposits + amount > depositLimit`. This asymmetry means the ETH deposit limit is never enforced for the marginal deposit that crosses the boundary.

---

### Title
ETH Deposit Limit Check Omits Deposit Amount, Allowing Any Depositor to Exceed the Protocol Cap — (File: `contracts/LRTDepositPool.sol`)

### Summary
`LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit()` applies an asymmetric check: for LSTs it correctly tests `totalAssetDeposits + amount > depositLimit`, but for ETH it only tests `totalAssetDeposits > depositLimit`, omitting the incoming `amount`. Any depositor can push ETH deposits beyond the configured cap in a single call whenever the running total is at or below the limit.

### Finding Description
`_beforeDeposit()` calls `_checkIfDepositAmountExceedesCurrentLimit()` before minting rsETH:

```solidity
// contracts/LRTDepositPool.sol  L676-682
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← missing + amount
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
``` [1](#0-0) 

`totalAssetDeposits` is the pre-deposit total. For ETH the function returns `true` (revert) only when the total **already** exceeds the limit. When `totalAssetDeposits == depositLimit`, the expression `depositLimit > depositLimit` is `false`, so the check passes and the deposit is accepted, pushing the total to `depositLimit + amount`.

The entry path is fully unprivileged:

```
depositETH() [public, payable]
  → _beforeDeposit()
    → _checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, msg.value)
      → returns false  ← incorrect when totalAssets == limit
  → _mintRsETH()      ← rsETH minted, limit exceeded
``` [2](#0-1) [3](#0-2) 

### Impact Explanation
The deposit limit is the protocol's primary safety cap on ETH exposure (EigenLayer strategy capacity, slashing risk, liquidity constraints). Bypassing it allows the protocol to accept more ETH than it is designed to handle. Any depositor can exceed the cap by exactly one deposit's worth of ETH per transaction, and can repeat this indefinitely as long as `totalAssetDeposits <= depositLimit` at the time of each call. This constitutes a **Low — contract fails to deliver promised returns** (the cap guarantee is broken), with potential escalation to **Medium — temporary freezing of funds** if the excess ETH cannot be delegated to EigenLayer strategies due to capacity limits.

### Likelihood Explanation
High. The condition `totalAssetDeposits == depositLimit` is reachable in normal operation (the limit is designed to be hit). No special privileges, front-running, or external dependencies are required — any ETH depositor triggers the bypass automatically.

### Recommendation
Apply the same `+ amount` inclusion used for LSTs:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
``` [4](#0-3) 

### Proof of Concept
1. Admin sets ETH deposit limit to `L` via `LRTConfig`.
2. Through normal deposits, `getTotalAssetDeposits(ETH_TOKEN)` reaches exactly `L`.
3. Attacker calls `depositETH{value: Y}(0, "")` for any `Y > 0`.
4. `_checkIfDepositAmountExceedesCurrentLimit` evaluates `L > L` → `false` → no revert.
5. `_mintRsETH` executes; total ETH deposits become `L + Y`, exceeding the configured cap.
6. Step 3–5 can be repeated in subsequent blocks as long as `totalAssetDeposits <= L` at call time (e.g., if assets are moved to NodeDelegators, reducing the pool balance counted by `getTotalAssetDeposits`).

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
