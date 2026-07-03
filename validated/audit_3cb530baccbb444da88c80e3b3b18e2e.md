### Title
Unprotected `initialize2()` Reinitializer Allows Any Caller to Consume the Upgrade Slot and Corrupt `lastNonce` - (File: contracts/NodeDelegator.sol)

### Summary
`NodeDelegator.initialize2()` carries no access-control modifier. Any external caller can invoke it before the protocol admin does, permanently consuming the `reinitializer(2)` slot and locking `lastNonce` to whatever `cumulativeWithdrawalsQueued` returns at that moment. Because `reinitializer(2)` can only succeed once, the admin loses the ability to set `lastNonce` to the intended value.

### Finding Description
`NodeDelegator` follows a split-initialization pattern: `initialize()` (version 1) sets up the core state, and `initialize2()` (version 2) snapshots the EigenLayer withdrawal nonce into the private variable `lastNonce`. [1](#0-0) 

```solidity
function initialize(address lrtConfigAddr) external initializer { ... }   // version 1

function initialize2() external reinitializer(2) {                         // version 2
    lastNonce = _getNonce();
}
```

Every other multi-step initializer in the codebase is gated:

- `LRTWithdrawalManager.initialize2()` — `onlyRole(LRTConstants.UNLOCKED_WITHDRAWAL_INITIALIZER)` [2](#0-1) 
- `LRTWithdrawalManager.initialize3()` — `onlyLRTManager` [3](#0-2) 
- `RSETH.reinitialize()` — `onlyLRTManager` [4](#0-3) 

`NodeDelegator.initialize2()` is the sole exception — it has **no modifier at all**. [5](#0-4) 

`_getNonce()` reads `delegationManager.cumulativeWithdrawalsQueued(address(this))`, the cumulative count of withdrawals ever queued by this NDC. [6](#0-5) 

### Impact Explanation
Once `initialize2()` is called by anyone, `_initialized` is set to `2` by the OZ `reinitializer` modifier and the function can never be called again. [7](#0-6) 

If an attacker front-runs the admin and calls `initialize2()` at a time when `cumulativeWithdrawalsQueued` differs from the value the admin intended to snapshot, `lastNonce` is permanently set to the wrong value. The admin has no recourse: the reinitializer slot is consumed and cannot be re-executed. Any downstream logic that compares the live nonce against `lastNonce` to detect new withdrawals or to emit correctly-indexed `WithdrawalQueued` events will operate on a corrupted baseline, potentially causing withdrawal-queue desync or incorrect nonce accounting for the NDC's EigenLayer withdrawal lifecycle.

**Impact class:** Low — contract fails to deliver promised initialization state; no direct fund loss, but the withdrawal-nonce baseline is permanently corrupted for the affected NDC.

### Likelihood Explanation
The window exists from the moment `initialize()` is called until the admin calls `initialize2()`. Any unprivileged EOA or bot can monitor the mempool for the proxy deployment / upgrade transaction and immediately call `initialize2()` in the same block or the next one. No special permissions, capital, or prior state are required.

### Recommendation
Add an access-control modifier to `initialize2()`, consistent with every other reinitializer in the codebase:

```solidity
function initialize2() external reinitializer(2) onlyLRTAdmin {
    lastNonce = _getNonce();
}
```

Alternatively, call `initialize2()` atomically inside the same upgrade transaction so no external caller can interpose.

### Proof of Concept
1. Protocol deploys `NodeDelegator` proxy and calls `initialize(lrtConfigAddr)` → `_initialized = 1`.
2. Before the admin calls `initialize2()`, attacker calls `NodeDelegator(proxy).initialize2()`.
3. OZ `reinitializer(2)` passes (`_initialized == 1 < 2`); `lastNonce` is set to the current `cumulativeWithdrawalsQueued` value (e.g., `0` if no withdrawals have been queued yet, or some stale value if they have).
4. `_initialized` is now `2`. Any subsequent call to `initialize2()` by the admin reverts with `"Initializable: contract is already initialized"`.
5. `lastNonce` is permanently locked to the attacker-chosen snapshot, corrupting the NDC's withdrawal-nonce baseline for the lifetime of the proxy.

### Citations

**File:** contracts/NodeDelegator.sol (L63-77)
```text
    /// @dev Initializes the contract
    /// @param lrtConfigAddr LRT config address
    function initialize(address lrtConfigAddr) external initializer {
        UtilLib.checkNonZeroAddress(lrtConfigAddr);
        __Pausable_init();
        __ReentrancyGuard_init();

        lrtConfig = ILRTConfig(lrtConfigAddr);

        emit UpdatedLRTConfig(lrtConfigAddr);
    }

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

**File:** contracts/LRTWithdrawalManager.sol (L126-129)
```text
    function initialize3(uint256 unlockedWithdrawalsCountSFRXETH) external reinitializer(3) onlyLRTManager {
        address sfrxETHAddress = 0xac3E018457B222d93114458476f3E3416Abbe38F;
        unlockedWithdrawalsCount[sfrxETHAddress] = unlockedWithdrawalsCountSFRXETH;
    }
```

**File:** contracts/RSETH.sol (L109-117)
```text
    function reinitialize(uint256 _periodStartTime, address _custodyAddress) external reinitializer(2) onlyLRTManager {
        if (_periodStartTime > block.timestamp || _periodStartTime <= block.timestamp - 1 days) {
            revert PeriodStartTimeShouldBeWithin24Hours();
        }
        periodStartTime = _periodStartTime;
        emit PeriodStartTimeSet(_periodStartTime);

        _setCustodyAddress(_custodyAddress);
    }
```

**File:** lib/openzeppelin-contracts-upgradeable/contracts/proxy/utils/Initializable.sol (L119-126)
```text
    modifier reinitializer(uint8 version) {
        require(!_initializing && _initialized < version, "Initializable: contract is already initialized");
        _initialized = version;
        _initializing = true;
        _;
        _initializing = false;
        emit Initialized(version);
    }
```
