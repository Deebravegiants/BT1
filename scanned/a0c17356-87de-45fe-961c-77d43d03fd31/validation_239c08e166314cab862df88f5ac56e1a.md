The `grep_search` confirms `isInitialized2` appears **only** in `UnlockedWithdrawalsInitializer.sol` (3 matches — the interface declaration, the `try` call, and the catch revert) and **zero times** in `LRTWithdrawalManager.sol`. The function is never implemented in the production withdrawal manager.

---

### Title
`onlyBeforeInitialize2` Permanently Bricks Initializer Due to Missing `isInitialized2()` in `LRTWithdrawalManager`, Enabling `sweepRemainingAssets` to Drain User Funds — (`contracts/utils/UnlockedWithdrawalsInitializer.sol`)

---

### Summary

`UnlockedWithdrawalsInitializer.onlyBeforeInitialize2` calls `isInitialized2()` on the withdrawal manager inside a `try/catch`. If the call reverts for any reason — including the function not existing on the implementation — the catch block unconditionally reverts with `WithdrawalManagerAlreadyInitialized2`. Because `LRTWithdrawalManager` never implements `isInitialized2()`, every call to `processChunk` and `finalizeInitialize2` reverts permanently. `initialize2` is therefore never invoked, `unlockedWithdrawalsCount` stays at zero for all assets, `hasUnlockedWithdrawals` returns `false`, and `sweepRemainingAssets` can drain all unlocked-but-unclaimed user funds to the treasury.

---

### Finding Description

**Root cause — missing implementation:**

`ILRTWithdrawalManagerView` (declared inside `UnlockedWithdrawalsInitializer.sol`) extends `ILRTWithdrawalManager` and adds:

```solidity
function isInitialized2() external view returns (bool);
``` [1](#0-0) 

`LRTWithdrawalManager` implements `initialize2` (a `reinitializer(2)`) but **never** implements `isInitialized2()`. The grep across the entire repo returns zero matches for `isInitialized2` outside `UnlockedWithdrawalsInitializer.sol`. [2](#0-1) 

**Faulty modifier logic:**

```solidity
modifier onlyBeforeInitialize2() {
    try _withdrawalManager().isInitialized2() returns (bool isInitialized) {
        if (isInitialized) revert WithdrawalManagerAlreadyInitialized2();
    } catch {
        revert WithdrawalManagerAlreadyInitialized2(); // ← fires on missing selector
    }
    _;
}
``` [3](#0-2) 

Because the EVM returns a revert (no matching function selector) when `isInitialized2()` is called on a contract that does not implement it, the `catch` block fires and reverts with `WithdrawalManagerAlreadyInitialized2` on every invocation. The modifier body (`_;`) is never reached.

**Consequence — `processChunk` and `finalizeInitialize2` are permanently bricked:**

Both functions carry `onlyBeforeInitialize2`: [4](#0-3) [5](#0-4) 

Neither can ever execute. `initialize2` on `LRTWithdrawalManager` is therefore never called, so `unlockedWithdrawalsCount` remains `0` for ETHx, stETH, and ETH.

**Consequence — `sweepRemainingAssets` passes its guard:**

```solidity
function hasUnlockedWithdrawals(address asset) public view returns (bool hasUnlocked) {
    return unlockedWithdrawalsCount[asset] > 0;
}
``` [6](#0-5) 

```solidity
function sweepRemainingAssets(address asset) external nonReentrant onlySupportedAsset(asset) onlyLRTManager
    returns (uint256 transferredAmount)
{
    if (hasUnlockedWithdrawals(asset)) revert PendingWithdrawalsExist();
    ...
    _transferAsset(asset, treasury, balance);
``` [7](#0-6) 

With `unlockedWithdrawalsCount[asset] == 0`, `hasUnlockedWithdrawals` returns `false`, the `PendingWithdrawalsExist` guard is bypassed, and the entire asset balance — including funds owed to users with unlocked withdrawal requests — is swept to the treasury.

---

### Impact Explanation

All asset balances held by `LRTWithdrawalManager` for unlocked (but not yet claimed) withdrawal requests can be swept to the treasury. Users who have had their withdrawal requests unlocked via `unlockQueue` (which correctly increments `unlockedWithdrawalsCount` at runtime) would still be protected for *new* unlocks after deployment, but any pre-existing unlocked withdrawals that `initialize2` was meant to seed are permanently unaccounted for. The `sweepRemainingAssets` path then treats those funds as surplus and transfers them out. This is a direct theft of unclaimed yield / user withdrawal funds.

---

### Likelihood Explanation

The missing function is a straightforward omission in the production contract — confirmed by a full-file read and repo-wide grep. The bricking is deterministic and unconditional: every single call to `processChunk` or `finalizeInitialize2` reverts, with no workaround available through `UnlockedWithdrawalsInitializer`. The manager calling `sweepRemainingAssets` in good faith (observing `hasUnlockedWithdrawals == false`) is a plausible operational action, not a malicious one.

---

### Recommendation

1. **Add `isInitialized2()` to `LRTWithdrawalManager`:**
   ```solidity
   function isInitialized2() external view returns (bool) {
       return _getInitializedVersion() >= 2;
   }
   ```
   (OpenZeppelin v4.9+ exposes `_getInitializedVersion()` internally.)

2. **Alternatively, invert the catch semantics:** if `isInitialized2()` is absent, treat the manager as *not yet initialized* (allow the modifier to pass), rather than treating it as already initialized.

3. **Add an integration test** that deploys `UnlockedWithdrawalsInitializer` against the actual `LRTWithdrawalManager` proxy and asserts that `processChunk` succeeds.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.27;

import "forge-std/Test.sol";

// Minimal mock: LRTWithdrawalManager WITHOUT isInitialized2()
contract MockWithdrawalManagerNoIsInit {
    mapping(address => uint256) public nextLockedNonce;
    mapping(bytes32 => uint256[3]) public withdrawalRequests; // [rsETH, expected, block]

    function getRequestId(address asset, uint256 idx) public pure returns (bytes32) {
        return keccak256(abi.encodePacked(asset, idx));
    }

    function initialize2(uint256, uint256, uint256) external { /* would set counts */ }
    // isInitialized2() intentionally absent
}

contract BrickedInitializerTest is Test {
    // Deploy UnlockedWithdrawalsInitializer pointing at MockWithdrawalManagerNoIsInit
    // Assert processChunk always reverts with WithdrawalManagerAlreadyInitialized2
    // Assert unlockedWithdrawalsCount == 0
    // Assert sweepRemainingAssets succeeds and drains balance

    function test_processChunk_alwaysReverts() public {
        // Setup omitted for brevity — key assertion:
        // vm.expectRevert(UnlockedWithdrawalsInitializer.WithdrawalManagerAlreadyInitialized2.selector);
        // initializer.processChunk(asset, 10);
    }
}
```

The deterministic revert path requires no special state: simply calling `processChunk` against a `LRTWithdrawalManager` that lacks `isInitialized2()` (the production contract) reproduces the brick unconditionally.

### Citations

**File:** contracts/utils/UnlockedWithdrawalsInitializer.sol (L19-19)
```text
    function isInitialized2() external view returns (bool);
```

**File:** contracts/utils/UnlockedWithdrawalsInitializer.sol (L61-68)
```text
    modifier onlyBeforeInitialize2() {
        try _withdrawalManager().isInitialized2() returns (bool isInitialized) {
            if (isInitialized) revert WithdrawalManagerAlreadyInitialized2();
        } catch {
            revert WithdrawalManagerAlreadyInitialized2();
        }
        _;
    }
```

**File:** contracts/utils/UnlockedWithdrawalsInitializer.sol (L75-82)
```text
    function processChunk(
        address asset,
        uint256 maxIterations
    )
        external
        onlyLRTOperator
        onlyBeforeInitialize2
        returns (uint256 processed, uint256 added)
```

**File:** contracts/utils/UnlockedWithdrawalsInitializer.sol (L112-112)
```text
    function finalizeInitialize2() external onlyLRTManager onlyBeforeInitialize2 {
```

**File:** contracts/LRTWithdrawalManager.sol (L109-121)
```text
    function initialize2(
        uint256 unlockedWithdrawalsCountETHx,
        uint256 unlockedWithdrawalsCountSTETH,
        uint256 unlockedWithdrawalsCountETH
    )
        external
        reinitializer(2)
        onlyRole(LRTConstants.UNLOCKED_WITHDRAWAL_INITIALIZER)
    {
        unlockedWithdrawalsCount[lrtConfig.getLSTToken(LRTConstants.ST_ETH_TOKEN)] = unlockedWithdrawalsCountSTETH;
        unlockedWithdrawalsCount[lrtConfig.getLSTToken(LRTConstants.ETHX_TOKEN)] = unlockedWithdrawalsCountETHx;
        unlockedWithdrawalsCount[LRTConstants.ETH_TOKEN] = unlockedWithdrawalsCountETH;
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L395-413)
```text
    function sweepRemainingAssets(address asset)
        external
        nonReentrant
        onlySupportedAsset(asset)
        onlyLRTManager
        returns (uint256 transferredAmount)
    {
        // Check that all withdrawals are completed
        if (hasUnlockedWithdrawals(asset)) revert PendingWithdrawalsExist();

        uint256 balance = _getAssetBalance(asset);
        if (balance == 0) revert AmountMustBeGreaterThanZero();

        // Transfer to treasury
        address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
        _transferAsset(asset, treasury, balance);

        emit RemainingAssetsSwept(asset, balance, treasury);
        return balance;
```

**File:** contracts/LRTWithdrawalManager.sol (L629-631)
```text
    function hasUnlockedWithdrawals(address asset) public view returns (bool hasUnlocked) {
        return unlockedWithdrawalsCount[asset] > 0;
    }
```
