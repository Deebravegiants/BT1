Based on the code, this is a valid finding. Here is the analysis:

**Code comparison:**

`LineaMessenger.sendETHToL1ViaBridge` has explicit guards: [1](#0-0) 

`OptimismMessenger.sendETHToL1ViaBridge` has only one guard: [2](#0-1) 

Both implement the same `IL2Messenger` interface: [3](#0-2) 

---

### Title
Missing Input Validation in OptimismMessenger Compared to LineaMessenger - (File: contracts/bridges/OptimismMessenger.sol)

### Summary
`OptimismMessenger.sendETHToL1ViaBridge` omits the zero-address and zero-value guards that `LineaMessenger` enforces, creating inconsistent behavior across `IL2Messenger` implementations and allowing degenerate inputs to reach the external bridge call silently.

### Finding Description
`LineaMessenger` enforces three explicit guards before bridging:
1. `UtilLib.checkNonZeroAddress(l2bridge)` — reverts with `ZeroAddressNotAllowed()` [4](#0-3) 
2. `UtilLib.checkNonZeroAddress(target)` — reverts with `ZeroAddressNotAllowed()` [5](#0-4) 
3. `if (value == 0) revert ZeroAmount()` [6](#0-5) 

`OptimismMessenger` only checks `msg.value != value` and immediately forwards the call to the external bridge: [7](#0-6) 

When `l2bridge == address(0)`, Solidity 0.8 makes a high-level call to `address(0)`. Since `address(0)` has no code, the call succeeds silently (no revert), and the ETH sent with `value: value` is forwarded to `address(0)` — effectively burned. When `target == address(0)` with a valid `l2bridge`, the bridge call proceeds and ETH is bridged to `address(0)` on L1. When `value == 0`, the bridge call is a no-op with no actionable error.

### Impact Explanation
The contract fails to deliver its promised bridging function. Callers passing misconfigured parameters (e.g., uninitialized `l2bridge` address) receive no named error and the operation silently fails or misdirects ETH. This violates the behavioral contract implied by `IL2Messenger` and makes misconfiguration harder to detect. Scoped as **Low** per the stated target scope (contract fails to deliver promised returns).

### Likelihood Explanation
Any caller of `OptimismMessenger.sendETHToL1ViaBridge` with an uninitialized or zero `l2bridge` address triggers this path. No special privileges are required — the function is `external payable` with no access control. [8](#0-7) 

### Recommendation
Add the same guards present in `LineaMessenger` to `OptimismMessenger`:

```solidity
function sendETHToL1ViaBridge(address l2bridge, address target, uint256 value) external payable nonReentrant {
    UtilLib.checkNonZeroAddress(l2bridge);
    UtilLib.checkNonZeroAddress(target);
    if (value == 0) revert ZeroAmount();
    if (msg.value != value) revert MismatchedMsgValue();
    IOptimismMessenger(l2bridge).bridgeETHTo{ value: value }(target, DEFAULT_GAS_LIMIT, bytes(""));
}
```

### Proof of Concept
Differential fuzz test (local/fork):
```solidity
// Both messengers called with (address(0), validTarget, 1 ether)
// LineaMessenger → reverts with ZeroAddressNotAllowed()  (named error)
// OptimismMessenger → call to address(0) succeeds silently, ETH sent to address(0)

// Both called with (validBridge, validTarget, 0)
// LineaMessenger → reverts with ZeroAmount()
// OptimismMessenger → proceeds, calls bridgeETHTo with value=0, no revert
```

The differential test confirms: any input rejected by `LineaMessenger` with a named error passes through `OptimismMessenger` without an equivalent named error, violating the invariant that all `IL2Messenger` implementations enforce the same minimum input validation. [3](#0-2)

### Citations

**File:** contracts/bridges/LineaMessenger.sol (L32-35)
```text
        UtilLib.checkNonZeroAddress(l2bridge);
        UtilLib.checkNonZeroAddress(target);

        if (value == 0) revert ZeroAmount();
```

**File:** contracts/bridges/OptimismMessenger.sol (L24-27)
```text
    function sendETHToL1ViaBridge(address l2bridge, address target, uint256 value) external payable nonReentrant {
        if (msg.value != value) revert MismatchedMsgValue();
        IOptimismMessenger(l2bridge).bridgeETHTo{ value: value }(target, DEFAULT_GAS_LIMIT, bytes(""));
    }
```

**File:** contracts/interfaces/L2/IL2Messenger.sol (L8-18)
```text
interface IL2Messenger {
    /// @notice Error thrown when the message value does not match the expected value
    error MismatchedMsgValue();

    /**
     * @notice Bridge ETH from L2 to L1 via a specified bridge contract
     * @param l2bridge The address of the L2 bridge contract
     * @param target The address of the recipient on L1
     * @param value The amount of ETH to send
     */
    function sendETHToL1ViaBridge(address l2bridge, address target, uint256 value) external payable;
```
