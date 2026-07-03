The core code is now fully visible. Let me analyze the exact logic.

**ETH path** (`contracts/LRTDepositPool.sol`, line 679):
```solidity
return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
```
The incoming `amount` is **completely ignored**. The check only asks "is the current total already over the limit?"

**ERC20 path** (line 681):
```solidity
return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
```
Correctly includes the incoming deposit amount.

This is a real, concrete bug — not just a boundary inconsistency. The ETH deposit limit is structurally non-functional: any user can deposit any amount of ETH as long as `totalAssetDeposits` is currently at or below the limit. The `amount` parameter passed in from `msg.value` is silently discarded for the ETH branch.

---

### Title
ETH Deposit Limit Completely Unenforced Due to Missing `amount` in Limit Check — (`contracts/LRTDepositPool.sol`)

### Summary
`_checkIfDepositAmountExceedesCurrentLimit` uses two different comparison expressions for ETH vs ERC20. The ETH branch omits the incoming deposit `amount` from the check, making the ETH deposit cap entirely ineffective for any single deposit that does not find the total already over the limit.

### Finding Description
In `LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit`:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← amount ignored
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← correct
}
``` [1](#0-0) 

For ETH, the function returns `true` (i.e., "limit exceeded, revert") only when `totalAssetDeposits` **already** exceeds the limit before the deposit. The new `amount` is never added to `totalAssetDeposits` in the comparison. Consequently:

- If `totalAssetDeposits = 50 ETH` and `depositLimit = 100 ETH`, a user calling `depositETH{value: 10_000 ether}(...)` passes the check (50 > 100 is false), and the full 10,000 ETH is accepted.
- The limit is only enforced on the *next* deposit after the total has already been pushed over — and even then, only if the total strictly exceeds (not equals) the limit.

The ERC20 path correctly computes `totalAssetDeposits + amount > limit`, blocking any deposit that would push the total over the cap.

The entry point is the public `depositETH` function:

```solidity
function depositETH(uint256 minRSETHAmountExpected, string calldata referralId)
    external payable nonReentrant whenNotPaused onlySupportedAsset(LRTConstants.ETH_TOKEN)
{
    uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);
    _mintRsETH(rsethAmountToMint);
    emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
}
``` [2](#0-1) 

`_beforeDeposit` calls `_checkIfDepositAmountExceedesCurrentLimit(LRTConstants.ETH_TOKEN, msg.value)`, but the ETH branch discards `msg.value`. [3](#0-2) 

`updateAssetDepositLimit` in `LRTConfig` has no lower-bound validation and is callable by any MANAGER:

```solidity
function updateAssetDepositLimit(address asset, uint256 depositLimit)
    external onlyRole(LRTConstants.MANAGER) onlySupportedAsset(asset)
{
    depositLimitByAsset[asset] = depositLimit;
    emit AssetDepositLimitUpdate(asset, depositLimit);
}
``` [4](#0-3) 

### Impact Explanation
The ETH deposit cap is completely bypassed by any single deposit. A user can deposit an arbitrarily large amount of ETH in one transaction as long as the current total has not already exceeded the limit. This violates the protocol's stated risk management invariant (deposit limits exist to cap exposure). Over-depositing beyond the intended limit can cause the protocol to hold more ETH than EigenLayer strategies are configured to absorb, potentially leaving ETH stranded in the deposit pool or NDCs — a temporary freezing of funds scenario. It also means the MANAGER's ability to cap ETH inflows (e.g., during a risk event) is entirely ineffective.

### Likelihood Explanation
The bug is present in unmodified production code and requires no special role or precondition. Any user calling `depositETH` with a large `msg.value` while `totalAssetDeposits < depositLimit` will bypass the cap. No front-running, governance capture, or key compromise is needed.

### Recommendation
Add `amount` to the ETH comparison, mirroring the ERC20 branch:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

### Proof of Concept
```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.27;

// Foundry fork test (local/private testnet)
// Setup: deploy LRTConfig + LRTDepositPool with ETH_TOKEN supported,
//        depositLimit = 100 ether, totalAssetDeposits = 0.

function test_ETHDepositLimitBypassed() public {
    // Precondition: limit is 100 ETH, nothing deposited yet
    assertEq(lrtConfig.depositLimitByAsset(ETH_TOKEN), 100 ether);
    assertEq(depositPool.getTotalAssetDeposits(ETH_TOKEN), 0);

    // Attacker deposits 10x the limit in one call
    vm.deal(attacker, 1000 ether);
    vm.prank(attacker);
    depositPool.depositETH{value: 1000 ether}(0, "");

    // Total now far exceeds the 100 ETH limit — no revert occurred
    assertGt(depositPool.getTotalAssetDeposits(ETH_TOKEN), 100 ether);

    // Equivalent ERC20 deposit of 1000 tokens against a 100-token limit WOULD revert:
    vm.expectRevert(ILRTDepositPool.MaximumDepositLimitReached.selector);
    depositPool.depositAsset(stETH, 1000 ether, 0, "");
}
```

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

**File:** contracts/LRTConfig.sol (L123-133)
```text
    function updateAssetDepositLimit(
        address asset,
        uint256 depositLimit
    )
        external
        onlyRole(LRTConstants.MANAGER)
        onlySupportedAsset(asset)
    {
        depositLimitByAsset[asset] = depositLimit;
        emit AssetDepositLimitUpdate(asset, depositLimit);
    }
```
