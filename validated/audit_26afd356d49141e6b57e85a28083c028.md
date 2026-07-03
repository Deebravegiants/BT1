### Title
ETH Deposit Limit Check Omits Incoming Amount, Allowing Deposit Cap Bypass - (File: contracts/LRTDepositPool.sol)

### Summary
`_checkIfDepositAmountExceedesCurrentLimit` applies an asymmetric guard: for ERC20 assets it correctly adds the incoming `amount` to `totalAssetDeposits` before comparing against the cap, but for ETH it omits `amount` entirely. The ETH branch therefore only reverts if the cap is already exceeded before the deposit, never if the deposit itself would push the total over the cap. Any unprivileged depositor can call `depositETH` and bypass the ETH deposit limit in a single transaction.

### Finding Description
In `LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit` (line 676–682):

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← amount not added
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← correct
}
```

The ETH branch evaluates `totalAssetDeposits > limit` instead of `totalAssetDeposits + amount > limit`. The incoming deposit value (`msg.value`) is never factored into the ETH cap check. The function is called from `_beforeDeposit`, which is the sole guard invoked by `depositETH` before minting rsETH. [1](#0-0) 

The ERC20 path correctly includes `amount`, confirming the ETH omission is unintentional. [2](#0-1) 

### Impact Explanation
**Medium – Temporary freezing of funds / Protocol insolvency.**

The ETH deposit cap (`depositLimitByAsset`) is a risk-management control. With the broken check, a single depositor can send an arbitrarily large ETH value (e.g., 10 000 ETH) when `totalAssetDeposits` is just 1 wei below the cap. The check returns `false` (not exceeded), the deposit proceeds, and rsETH is minted at the current exchange rate for the full over-limit amount. This:

1. Inflates rsETH supply beyond the protocol's intended backing, degrading the rsETH/ETH ratio for all holders.
2. Defeats the cap that protects against concentration risk in EigenLayer strategies.
3. Can cause the protocol to hold more ETH than it can safely deploy, or mint more rsETH than it can redeem, approaching insolvency.

### Likelihood Explanation
**High.** The entry point `depositETH` is public, requires no role, and is the primary user-facing deposit function. No preconditions beyond having ETH are needed. The broken branch is hit on every ETH deposit when `totalAssetDeposits ≤ depositLimit`, which is the normal operating state of the protocol. [3](#0-2) 

### Recommendation
Add `amount` to the ETH branch, mirroring the ERC20 logic:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

This makes the ETH cap check consistent with the ERC20 cap check and closes the bypass.

### Proof of Concept
Assume:
- `depositLimitByAsset(ETH_TOKEN) = 1000 ether`
- `getTotalAssetDeposits(ETH_TOKEN) = 999 ether` (one wei below cap)

Attacker calls `depositETH{value: 10_000 ether}(0, "")`:

1. `_beforeDeposit(ETH_TOKEN, 10_000 ether, 0)` is called.
2. `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, 10_000 ether)` evaluates `999 ether > 1000 ether` → `false`.
3. Guard does **not** revert.
4. `getRsETHAmountToMint` computes rsETH for 10 000 ETH at the current price.
5. `_mintRsETH` mints rsETH to the attacker.
6. Protocol now holds 10 999 ETH against a cap of 1 000 ETH; rsETH supply is inflated by 10 000 ETH worth of tokens. [1](#0-0) [4](#0-3)

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

**File:** contracts/LRTDepositPool.sol (L657-669)
```text
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

**File:** contracts/LRTDepositPool.sol (L684-690)
```text
    /// @dev private function to mint rseth
    /// @param rsethAmountToMint Amount of rseth minted
    function _mintRsETH(uint256 rsethAmountToMint) private {
        address rsethToken = lrtConfig.rsETH();
        // mint rseth for user
        IRSETH(rsethToken).mint(msg.sender, rsethAmountToMint);
    }
```
