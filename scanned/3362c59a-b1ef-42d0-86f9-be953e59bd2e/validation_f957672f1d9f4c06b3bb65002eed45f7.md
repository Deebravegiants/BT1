### Title
Unprotected `initialize2()` Reinitializer Allows Any Caller to Seize Initialization — (`contracts/NodeDelegator.sol`)

### Summary
`NodeDelegator.initialize2()` carries the `reinitializer(2)` modifier but **no access-control modifier**. Any external account can call it before the protocol admin does, permanently consuming the one-time reinitializer slot and setting `lastNonce` to an attacker-chosen timestamp value, while blocking the admin from ever executing the intended upgrade initialization.

### Finding Description
`NodeDelegator.initialize2()` is declared as:

```solidity
function initialize2() external reinitializer(2) {
    lastNonce = _getNonce();
}
``` [1](#0-0) 

`reinitializer(2)` guarantees the body executes **at most once** — the first caller wins and the slot is permanently consumed. Unlike every other multi-version initializer in the codebase, this function carries **no role guard**:

- `LRTWithdrawalManager.initialize2()` is gated by `onlyRole(LRTConstants.UNLOCKED_WITHDRAWAL_INITIALIZER)` [2](#0-1) 
- `LRTWithdrawalManager.initialize3()` is gated by `onlyLRTManager` [3](#0-2) 
- `LRTConverter.initialize2()` is gated by `onlyLRTAdmin` [4](#0-3) 

`NodeDelegator.initialize2()` has none of these guards. [1](#0-0) 

`_getNonce()` reads `cumulativeWithdrawalsQueued(address(this))` from the EigenLayer DelegationManager: [5](#0-4) 

`lastNonce` is a private storage variable whose value is consumed by internal withdrawal-queue accounting. [6](#0-5) 

### Impact Explanation
An attacker who calls `initialize2()` before the admin:

1. **Permanently blocks the admin** from executing the intended upgrade initialization — `reinitializer(2)` reverts on any subsequent call.
2. **Corrupts `lastNonce`** — the value is captured at the attacker's chosen block rather than the block the admin intended, desynchronizing the contract's internal nonce tracking from the actual EigenLayer withdrawal queue state.
3. Because `lastNonce` feeds withdrawal-queue event indexing used by off-chain infrastructure and potentially on-chain accounting, a stale or zero value can cause the NodeDelegator to misreport queued withdrawal indices, breaking the operator's ability to correctly track and complete EigenLayer unstaking flows.

**Impact: Low — Contract fails to deliver promised returns (withdrawal nonce tracking is corrupted; admin initialization path is permanently bricked for this upgrade version).**

### Likelihood Explanation
The upgrade transaction and the `initialize2()` call are separate transactions (non-atomic), exactly as described in the external report. Any mempool observer can front-run the admin's `initialize2()` call. No special privilege, capital, or prior state is required — a single `eth_sendRawTransaction` suffices. Likelihood is **Medium**.

### Recommendation
Add an access-control modifier consistent with the rest of the codebase:

```solidity
function initialize2() external reinitializer(2) onlyLRTAdmin {
    lastNonce = _getNonce();
}
```

Alternatively, perform the upgrade and initialization atomically via `upgradeAndCall()` so no window exists between deployment and initialization.

### Proof of Concept
1. Protocol admin submits an upgrade transaction pointing the proxy to the new `NodeDelegator` implementation.
2. Before the admin's follow-up `initialize2()` transaction is mined, an attacker observes it in the mempool and submits `nodeDelegator.initialize2()` with higher gas.
3. Attacker's transaction is mined first; `reinitializer(2)` sets `_initialized = 2` and writes `lastNonce = _getNonce()` (potentially 0 or a stale value).
4. Admin's `initialize2()` transaction reverts: `"Initializable: contract is already initialized"`.
5. The NodeDelegator is now permanently stuck at reinitializer version 2 with a corrupted `lastNonce`, and the admin has no recourse without deploying a new implementation with a `reinitializer(3)` fix. [1](#0-0)

### Citations

**File:** contracts/NodeDelegator.sol (L56-56)
```text
    uint256 private lastNonce;
```

**File:** contracts/NodeDelegator.sol (L75-77)
```text
    function initialize2() external reinitializer(2) {
        lastNonce = _getNonce();
    }
```

**File:** contracts/NodeDelegator.sol (L584-586)
```text
    function _getNonce() internal view returns (uint256) {
        return _getDelegationManager().cumulativeWithdrawalsQueued(address(this));
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L109-116)
```text
    function initialize2(
        uint256 unlockedWithdrawalsCountETHx,
        uint256 unlockedWithdrawalsCountSTETH,
        uint256 unlockedWithdrawalsCountETH
    )
        external
        reinitializer(2)
        onlyRole(LRTConstants.UNLOCKED_WITHDRAWAL_INITIALIZER)
```

**File:** contracts/LRTWithdrawalManager.sol (L126-129)
```text
    function initialize3(uint256 unlockedWithdrawalsCountSFRXETH) external reinitializer(3) onlyLRTManager {
        address sfrxETHAddress = 0xac3E018457B222d93114458476f3E3416Abbe38F;
        unlockedWithdrawalsCount[sfrxETHAddress] = unlockedWithdrawalsCountSFRXETH;
    }
```

**File:** contracts/LRTConverter.sol (L98-111)
```text
    function initialize2(
        address _withdrawalQueueAddress,
        address _stETHAddress,
        address _swEXITAddress,
        address _swETHAddress
    )
        external
        reinitializer(2)
        onlyLRTAdmin
    {
        __ReentrancyGuard_init();
        __initializeSwETH(_swEXITAddress, _swETHAddress);
        __initializeStETH(_withdrawalQueueAddress, _stETHAddress);
    }
```
