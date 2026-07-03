### Title
ETH Deposit Limit Bypass Due to Missing `amount` in Limit Check - (File: contracts/LRTDepositPool.sol)

### Summary
`_checkIfDepositAmountExceedesCurrentLimit` applies an asymmetric check: for ERC20 assets it correctly adds the incoming `amount` to `totalAssetDeposits` before comparing against the cap, but for ETH it omits `amount` entirely. Any depositor can call `depositETH` and push total ETH deposits arbitrarily above `depositLimitByAsset(ETH_TOKEN)`.

### Finding Description

In `LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit`:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)); // ← amount ignored
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← correct
}
``` [1](#0-0) 

For ERC20 assets the guard is `totalAssetDeposits + amount > limit` — the prospective new total is checked. For ETH the guard is `totalAssetDeposits > limit` — only the pre-deposit total is checked, and `amount` is never factored in.

Concrete scenario:
- `depositLimitByAsset(ETH_TOKEN)` = 1 000 ETH
- `totalAssetDeposits(ETH)` = 1 ETH (well below the cap)
- Attacker calls `depositETH{value: 10_000 ETH}(...)`
- Check: `1 > 1000` → `false` → deposit proceeds
- Post-deposit total: 10 001 ETH — 9 001 ETH above the intended cap

The entry path is `depositETH` → `_beforeDeposit` → `_checkIfDepositAmountExceedesCurrentLimit`. [2](#0-1) [3](#0-2) 

### Impact Explanation

The ETH deposit cap — a protocol-level safety parameter — is completely unenforceable. A single `depositETH` call can mint rsETH far beyond the intended limit, over-issuing rsETH relative to the protocol's risk-managed ETH capacity and violating the deposit ceiling invariant. Impact: **Low — contract fails to deliver promised returns** (deposit cap is not enforced for ETH), with potential escalation to Medium if the excess ETH cannot be safely deployed to EigenLayer strategies.

### Likelihood Explanation

Any unprivileged external caller can trigger this via the public `depositETH` function with no preconditions other than holding sufficient ETH. The ETH path is the primary deposit route for the protocol. Likelihood is **High**.

### Recommendation

Mirror the ERC20 branch for ETH:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
``` [4](#0-3) 

### Proof of Concept

1. Admin sets `depositLimitByAsset(ETH_TOKEN)` = 100 ether.
2. Protocol has 1 ether of existing ETH deposits (`totalAssetDeposits` = 1 ether).
3. Attacker calls `LRTDepositPool.depositETH{value: 10_000 ether}(0, "")`.
4. `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, 10_000 ether)` evaluates `1 ether > 100 ether` → `false`.
5. `_mintRsETH` mints rsETH for 10 000 ETH worth of value.
6. `getTotalAssetDeposits(ETH_TOKEN)` now returns 10 001 ether — 9 901 ether above the cap.
7. The deposit limit is bypassed entirely in a single transaction.

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
