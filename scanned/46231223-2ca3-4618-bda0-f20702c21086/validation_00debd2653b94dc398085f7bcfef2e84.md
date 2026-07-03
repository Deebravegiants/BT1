### Title
Missing Zero-Value Guard in `sendETHToL1ViaBridge` Allows Spurious Zero-ETH Bridge Calls — (`contracts/bridges/OptimismMessenger.sol`)

### Summary

`OptimismMessenger.sendETHToL1ViaBridge` lacks a `value == 0` revert, unlike its sibling `LineaMessenger`. A caller can invoke it with `value = 0` and `msg.value = 0`, passing the only guard and forwarding a zero-value call to the Optimism bridge.

### Finding Description

The sole guard in `OptimismMessenger` is:

```solidity
if (msg.value != value) revert MismatchedMsgValue();
``` [1](#0-0) 

When both `msg.value` and `value` are `0`, the condition is `false`, so no revert occurs. The function then calls:

```solidity
IOptimismMessenger(l2bridge).bridgeETHTo{ value: value }(target, DEFAULT_GAS_LIMIT, bytes(""));
``` [2](#0-1) 

This submits a zero-value bridge message to the Optimism L2 bridge. Compare with `LineaMessenger`, which explicitly guards against this:

```solidity
if (value == 0) revert ZeroAmount();
``` [3](#0-2) 

The missing check is a concrete, verifiable code deficiency in `OptimismMessenger` relative to the protocol's own established pattern.

### Impact Explanation

**Low — Contract fails to deliver promised returns, but doesn't lose value.**

A zero-value bridge call succeeds: no ETH is transferred to L1, L2 gas is consumed, and a bridge event is emitted for 0 ETH. This can confuse off-chain event monitors or L1 accounting systems that assume every bridge event carries a non-zero amount. No user funds are lost.

### Likelihood Explanation

Any external caller (no role required) can trigger this with a simple call: `sendETHToL1ViaBridge{value: 0}(l2bridge, target, 0)`. The Optimism standard bridge's `bridgeETHTo` does not universally revert on zero value at the contract level (it is a payable function with no explicit zero-value guard in the standard implementation), so the call can propagate. The root cause is the missing check in `OptimismMessenger` itself, not external dependency behavior.

### Recommendation

Add an explicit zero-value check mirroring `LineaMessenger`:

```solidity
if (value == 0) revert ZeroAmount();
```

Place it before the `msg.value != value` check in `sendETHToL1ViaBridge`. [4](#0-3) 

### Proof of Concept

```solidity
// In a local fork or unit test with a mock bridge that accepts zero value:
mockBridge.expectCall(target, 0, abi.encodeCall(IOptimismMessenger.bridgeETHTo, (target, 200_000, "")));
optimismMessenger.sendETHToL1ViaBridge{value: 0}(address(mockBridge), target, 0);
// Assert: call did NOT revert, mock bridge received bridgeETHTo with value=0
```

The call succeeds, the mock bridge records a `bridgeETHTo` invocation with `value = 0`, and no ETH is bridged — confirming the invariant violation.

### Citations

**File:** contracts/bridges/OptimismMessenger.sol (L24-27)
```text
    function sendETHToL1ViaBridge(address l2bridge, address target, uint256 value) external payable nonReentrant {
        if (msg.value != value) revert MismatchedMsgValue();
        IOptimismMessenger(l2bridge).bridgeETHTo{ value: value }(target, DEFAULT_GAS_LIMIT, bytes(""));
    }
```

**File:** contracts/bridges/LineaMessenger.sol (L35-35)
```text
        if (value == 0) revert ZeroAmount();
```
