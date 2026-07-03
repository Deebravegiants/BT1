Now I have all the code needed. Let me analyze both claims precisely.

### Title
ETH Deposit Limit Not Enforced — `_checkIfDepositAmountExceedesCurrentLimit` Ignores `msg.value` for ETH — (`contracts/LRTDepositPool.sol`)

---

### Summary

`_checkIfDepositAmountExceedesCurrentLimit` silently drops the `amount` parameter when `asset == LRTConstants.ETH_TOKEN`, making the ETH deposit cap unenforceable. Any depositor can bypass the ETH limit entirely, while `getAssetCurrentLimit` continues to advertise a non-zero (or zero) remaining capacity that bears no relationship to what is actually enforced.

---

### Finding Description

**`getAssetCurrentLimit`** (lines 402–409) computes the remaining capacity uniformly for all assets:

```solidity
return lrtConfig.depositLimitByAsset(asset) - totalAssetDeposits;
``` [1](#0-0) 

**`_checkIfDepositAmountExceedesCurrentLimit`** (lines 676–682) branches on asset type:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)); // amount ignored
}
return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // correct for ERC20
``` [2](#0-1) 

For ETH the check asks only *"has the total already exceeded the limit?"* — it never asks *"would adding this deposit exceed the limit?"*. The `amount` argument (which equals `msg.value` passed from `depositETH`) is discarded. [3](#0-2) 

The ERC20 path (`totalAssetDeposits + amount > depositLimitByAsset`) is correct and consistent with `getAssetCurrentLimit`; the off-by-one claim in the question does not hold for ERC20.

---

### Impact Explanation

- `getAssetCurrentLimit(ETH_TOKEN)` returns, e.g., `1 wei` (limit nearly full).
- A depositor calls `depositETH{value: 1000 ether}(...)`.
- The guard evaluates `totalAssetDeposits > depositLimitByAsset` → `false` → no revert.
- 1000 ETH is accepted and rsETH is minted, far beyond the configured cap.
- Even when `getAssetCurrentLimit` returns `0` (limit exactly reached), the same deposit succeeds because `totalAssetDeposits > depositLimitByAsset` is still `false` (equal, not greater).

The deposit limit — a core protocol invariant — is completely unenforced for native ETH. No funds are stolen, but the contract fails to deliver the promised deposit-cap guarantee.

**Scope match:** Low — Contract fails to deliver promised returns, but doesn't lose value.

---

### Likelihood Explanation

Any user depositing ETH when the pool is near or at its ETH limit triggers this. No special role, no front-running, no oracle manipulation required. The path is `depositETH` → `_beforeDeposit` → `_checkIfDepositAmountExceedesCurrentLimit`. [4](#0-3) 

---

### Recommendation

Include `amount` in the ETH branch, mirroring the ERC20 logic:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

---

### Proof of Concept

```solidity
// Foundry test (local, no fork needed)
function test_ETHLimitBypass() public {
    uint256 limit = 10 ether;
    // assume ETH is a supported asset with depositLimitByAsset = 10 ether
    // and totalAssetDeposits is currently 9.999... ether (1 wei below limit)
    // getAssetCurrentLimit returns 1 wei

    uint256 currentLimit = depositPool.getAssetCurrentLimit(LRTConstants.ETH_TOKEN);
    assertEq(currentLimit, 1); // 1 wei remaining

    // deposit 5 ETH — should revert with MaximumDepositLimitReached, but doesn't
    vm.deal(alice, 5 ether);
    vm.prank(alice);
    depositPool.depositETH{value: 5 ether}(0, "");

    // total now 9.999... + 5 ether >> limit; no revert occurred
    assert(depositPool.getTotalAssetDeposits(LRTConstants.ETH_TOKEN) > limit);
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
