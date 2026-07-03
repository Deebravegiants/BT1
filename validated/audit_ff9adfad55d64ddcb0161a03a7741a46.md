Audit Report

## Title
Wrong Variable Used in ETH Deposit Limit Check Allows Deposit Cap Bypass - (File: contracts/LRTDepositPool.sol)

## Summary
`_checkIfDepositAmountExceedesCurrentLimit` omits the incoming `amount` from the ETH branch's limit comparison, checking only `totalAssetDeposits > limit` instead of `totalAssetDeposits + amount > limit`. Any unprivileged caller can invoke `depositETH()` and deposit an arbitrarily large amount of ETH in a single transaction as long as the pre-existing total has not already crossed the cap, bypassing the governance-set deposit ceiling entirely.

## Finding Description
The root cause is a missing `+ amount` in the ETH branch of `_checkIfDepositAmountExceedesCurrentLimit`:

```solidity
// contracts/LRTDepositPool.sol L676-682
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // amount silently ignored
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // correct
}
``` [1](#0-0) 

The ERC-20 branch correctly adds `amount` to the running total before comparing against the limit. The ETH branch does not. Because `_beforeDeposit` reverts only when this function returns `true`, the ETH deposit limit is never triggered by the size of the incoming deposit — only by whether the pre-existing total has already exceeded the cap. [2](#0-1) 

The public entry point `depositETH` carries no role restriction and is callable by any address: [3](#0-2) 

## Impact Explanation
**Low — Contract fails to deliver promised returns, but doesn't lose value.**

The governance-set deposit limit is a risk-management invariant the contract explicitly promises to enforce. For ETH deposits, that invariant is silently broken: the protocol will accept ETH deposits of any size as long as the pre-existing total is below the cap. No direct fund loss occurs from the bypass itself; the slashing exposure that could follow is contingent on an external EigenLayer event and therefore does not independently satisfy a higher impact tier. The concrete, self-contained impact is that the contract fails to enforce its own deposit ceiling for ETH.

## Likelihood Explanation
`depositETH` is `external payable` with no access control. Any depositor who observes that `getTotalAssetDeposits(ETH_TOKEN)` is below the configured limit can immediately exploit the gap. No special privileges, timing windows, or victim interaction are required. The condition is trivially observable on-chain and repeatable across blocks.

## Recommendation
Add `amount` to the ETH branch to match the ERC-20 branch:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
``` [4](#0-3) 

## Proof of Concept
1. Governance sets `depositLimitByAsset(ETH_TOKEN) = 1000 ether`.
2. `getTotalAssetDeposits(ETH_TOKEN)` returns `999 ether`.
3. Attacker calls `depositETH{value: 10_000 ether}(0, "")`.
4. `_checkIfDepositAmountExceedesCurrentLimit` evaluates `999 ether > 1000 ether` → `false`; `amount` (`10_000 ether`) is never used.
5. `_beforeDeposit` does not revert; `10_000 ether` worth of rsETH is minted.
6. Protocol now holds `10_999 ether` — nearly 11× the intended cap — with no revert or event indicating the limit was breached.

**Foundry test sketch:**
```solidity
function test_ethDepositCapBypass() public {
    // set cap to 1000 ether, seed pool with 999 ether of prior deposits
    vm.deal(attacker, 10_000 ether);
    vm.prank(attacker);
    depositPool.depositETH{value: 10_000 ether}(0, "");
    assertGt(depositPool.getTotalAssetDeposits(ETH_TOKEN), 1000 ether);
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
