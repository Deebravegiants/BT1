Audit Report

## Title
ETH deposit cap bypass due to missing `+ amount` in `_checkIfDepositAmountExceedesCurrentLimit` — (`contracts/LRTDepositPool.sol`)

## Summary
The ETH branch of `_checkIfDepositAmountExceedesCurrentLimit` checks only whether the pre-deposit total already exceeds the cap, without adding the incoming `amount`. The ERC20 branch correctly includes `+ amount`. Any unprivileged depositor can push ETH TVL above the configured `depositLimitByAsset` cap by depositing when the total is at or near the limit.

## Finding Description
In `_checkIfDepositAmountExceedesCurrentLimit` ( [1](#0-0) ), the ETH branch returns `totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)` ( [2](#0-1) ) while the ERC20 branch returns `totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)` ( [3](#0-2) ). The ETH check only blocks deposits when the cap has **already** been exceeded; it never accounts for the incoming deposit amount.

The call path is fully unprivileged: `depositETH()` ( [4](#0-3) ) calls `_beforeDeposit()`, which calls `_checkIfDepositAmountExceedesCurrentLimit()` and reverts with `MaximumDepositLimitReached` only if it returns `true` ( [5](#0-4) ). Because the ETH branch omits `+ amount`, the revert never fires for a deposit that would push the total over the cap.

The inconsistency with `getAssetCurrentLimit` further confirms the bug: when `totalAssetDeposits == limit`, that function correctly returns `0` ( [6](#0-5) ), yet `_checkIfDepositAmountExceedesCurrentLimit` returns `false` for ETH, allowing the deposit.

## Impact Explanation
The protocol's per-asset TVL ceiling (`depositLimitByAsset`) is not enforced for ETH deposits. Any depositor can push ETH TVL above the configured cap. No funds are lost and the exchange rate is not diluted (real ETH backs the minted rsETH), so this matches **Low — Contract fails to deliver promised returns, but doesn't lose value**.

## Likelihood Explanation
No special role or privilege is required. Any user can trigger this by calling `depositETH` with any nonzero `msg.value` when `totalAssetDeposits` is at or near the limit. The condition is reachable in normal protocol operation whenever the ETH cap is close to full, and is repeatable by any depositor.

## Recommendation
Change the ETH branch to mirror the ERC20 branch by including `+ amount`:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
``` [7](#0-6) 

## Proof of Concept

```solidity
// Foundry unit test
function test_ETHCapBypass() public {
    uint256 cap = lrtConfig.depositLimitByAsset(LRTConstants.ETH_TOKEN);

    // Bring total ETH deposits to exactly the cap via prior deposits or mock
    // assertEq(depositPool.getAssetCurrentLimit(LRTConstants.ETH_TOKEN), 0);

    // This should revert with MaximumDepositLimitReached but succeeds:
    depositPool.depositETH{value: 1 ether}(0, "");

    // Total deposits now exceed cap
    assertGt(depositPool.getTotalAssetDeposits(LRTConstants.ETH_TOKEN), cap);
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
