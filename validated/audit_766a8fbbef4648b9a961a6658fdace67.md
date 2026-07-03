Audit Report

## Title
ETH Deposit Limit Bypass via Missing `amount` in Limit Check — (`contracts/LRTDepositPool.sol`)

## Summary
`_checkIfDepositAmountExceedesCurrentLimit` omits the `amount` parameter from its ETH branch, checking only whether the running total has already exceeded the cap rather than whether adding the new deposit would exceed it. Any unprivileged user can deposit arbitrary ETH beyond the configured cap. The ERC-20 path is correct; only native ETH is affected.

## Finding Description
`depositETH` passes `msg.value` as `depositAmount` to `_beforeDeposit` [1](#0-0) , which calls `_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)` and reverts on `true`. [2](#0-1) 

Inside that function the ETH branch is:
```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)); // amount ignored
}
``` [3](#0-2) 

The ERC-20 branch correctly includes `amount`:
```solidity
return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
``` [4](#0-3) 

The ETH check only asks "has the total already exceeded the limit?" — never "would this deposit push it over?" — so the guard returns `false` (no revert) for any deposit made while `totalAssetDeposits <= depositLimitByAsset`, regardless of how large `msg.value` is. Even when `getAssetCurrentLimit` returns `0` (limit exactly reached), the condition `totalAssetDeposits > limit` is still `false` (equal, not greater), so a deposit still succeeds. [5](#0-4) 

## Impact Explanation
The ETH deposit cap — a core protocol invariant — is completely unenforced. A depositor can supply any `msg.value` beyond the configured limit and receive rsETH in return. No funds are stolen and no accounting is corrupted, but the contract fails to deliver the promised deposit-cap guarantee.

**Severity: Low — Contract fails to deliver promised returns, but doesn't lose value.**

## Likelihood Explanation
No special role, no front-running, and no oracle manipulation is required. Any external caller invoking `depositETH` when `totalAssetDeposits <= depositLimitByAsset` triggers the bypass. The path is entirely public: `depositETH` → `_beforeDeposit` → `_checkIfDepositAmountExceedesCurrentLimit`. [6](#0-5) 

## Recommendation
Mirror the ERC-20 logic in the ETH branch:
```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

## Proof of Concept
```solidity
function test_ETHLimitBypass() public {
    // Setup: ETH limit = 10 ether, totalAssetDeposits = 9.999... ether (1 wei below limit)
    // getAssetCurrentLimit(ETH_TOKEN) == 1 wei

    uint256 limitBefore = depositPool.getAssetCurrentLimit(LRTConstants.ETH_TOKEN);
    assertEq(limitBefore, 1); // 1 wei remaining

    // Deposit 5 ETH — should revert MaximumDepositLimitReached, but does not
    vm.deal(alice, 5 ether);
    vm.prank(alice);
    depositPool.depositETH{value: 5 ether}(0, "");

    // Total now far exceeds limit; no revert occurred
    assert(depositPool.getTotalAssetDeposits(LRTConstants.ETH_TOKEN) > 10 ether);
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

**File:** contracts/LRTDepositPool.sol (L678-679)
```text
        if (asset == LRTConstants.ETH_TOKEN) {
            return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
```

**File:** contracts/LRTDepositPool.sol (L681-681)
```text
        return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
```
