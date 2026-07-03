### Title
gasLimit=0 in ScrollMessenger Causes L1 Relay Failure and Temporary ETH Escrow Lock — (File: contracts/bridges/ScrollMessenger.sol)

---

### Summary

`ScrollMessenger.sendETHToL1ViaBridge` hardcodes `gasLimit=0` when calling Scroll's native bridge. Unlike Optimism and Base messengers (which use `DEFAULT_GAS_LIMIT = 200_000`), Scroll's bridge interprets this literally as zero gas for L1 execution. When the L1ScrollMessenger attempts to relay the message, the call to the target contract fails out-of-gas. The ETH is held in L1ScrollMessenger escrow — it has already left L2 and is not yet accessible on L1 — until someone manually calls `replayMessage` on L1 with a correct gas limit.

---

### Finding Description

`RSETHPoolV2.bridgeAssets()` calls `IL2Messenger(messenger).sendETHToL1ViaBridge` forwarding the full `ethBalanceMinusFees` to the configured `messenger` contract. [1](#0-0) 

When the messenger is `ScrollMessenger`, `sendETHToL1ViaBridge` calls:

```solidity
IScrollMessenger(l2bridge).sendMessage{ value: value }(target, value, "", 0, msg.sender);
``` [2](#0-1) 

The fourth argument (`0`) is the `gasLimit` parameter, described in the interface as:

> "Gas limit required to complete the message relay on corresponding chain." [3](#0-2) 

Scroll's L2ScrollMessenger does **not** treat `gasLimit=0` as "use default." It encodes the value literally into the cross-chain message. On L1, the `L1ScrollMessenger.relayMessageWithProof` call forwards exactly 0 gas to the target (`l1VaultETHForL2Chain`). Since the target is a contract (not an EOA), its `receive()` function requires at least 2,300 gas (stipend) or more. With 0 gas forwarded, the call fails, emitting `FailedRelayedMessage`. The ETH is retained in L1ScrollMessenger escrow.

Compare with the other messengers, which all use an explicit non-zero gas limit: [4](#0-3) [5](#0-4) 

The developer comment "Gas limit is set to 0 to use the default gas limit" reflects a misunderstanding of Scroll's bridge semantics — there is no default fallback for `gasLimit=0`.

---

### Impact Explanation

After `bridgeAssets()` succeeds on L2:
- The ETH is **no longer in RSETHPoolV2** (deducted from pool balance, `address(this).balance` reduced).
- The ETH is **not yet in `l1VaultETHForL2Chain`** (relay failed).
- The ETH is **held in L1ScrollMessenger escrow**, inaccessible until `replayMessage` is called on L1 with a valid `gasLimit`.

This violates the invariant that bridged ETH must be accessible on exactly one chain at all times. The funds are temporarily frozen until a permissionless `replayMessage` call is made on L1. **Impact: Medium — Temporary freezing of funds.**

---

### Likelihood Explanation

`bridgeAssets()` is restricted to `BRIDGER_ROLE` and is called as part of normal, routine protocol operations (not an attack path). Every legitimate bridge operation on Scroll will trigger this failure. Likelihood is **high** given that the bug fires on every normal `bridgeAssets()` call when the Scroll messenger is configured.

---

### Recommendation

Replace the hardcoded `0` with an appropriate gas limit, consistent with the other messenger implementations:

```solidity
uint32 public constant DEFAULT_GAS_LIMIT = 200_000;

function sendETHToL1ViaBridge(address l2bridge, address target, uint256 value) external payable nonReentrant {
    if (msg.value != value) revert MismatchedMsgValue();
    IScrollMessenger(l2bridge).sendMessage{ value: value }(target, value, "", DEFAULT_GAS_LIMIT, msg.sender);
}
```

The gas limit should be calibrated to the actual gas cost of `l1VaultETHForL2Chain`'s `receive()` or fallback function. Note that Scroll charges an L2 fee proportional to `gasLimit`, so the `msg.value` forwarded must also cover this fee — the current implementation does not account for this fee either, which is a related but separate issue.

---

### Proof of Concept

1. Deploy a fork of Scroll L2 with the production `L2ScrollMessenger` at its canonical address.
2. Deploy `RSETHPoolV2` with `ScrollMessenger` as the `messenger`.
3. Fund `RSETHPoolV2` with ETH via `deposit()`.
4. Call `bridgeAssets()` from a `BRIDGER_ROLE` account.
5. Observe the L2 transaction succeeds and `BridgedETHToL1ViaNativeBridge` is emitted.
6. On the L1 fork, observe `L1ScrollMessenger.relayMessageWithProof` emits `FailedRelayedMessage` (out-of-gas on target call).
7. Assert `l1VaultETHForL2Chain.balance` is unchanged.
8. Assert `L1ScrollMessenger` holds the ETH in escrow (its balance increased).
9. Assert no L2-side refund was issued.
10. Call `L1ScrollMessenger.replayMessage(...)` with `gasLimit=200_000` to recover the funds.

### Citations

**File:** contracts/pools/RSETHPoolV2.sol (L292-298)
```text
        uint256 ethBalanceMinusFees = getETHBalanceMinusFees();

        IL2Messenger(messenger).sendETHToL1ViaBridge{ value: ethBalanceMinusFees }(
            l2Bridge, l1VaultETHForL2Chain, ethBalanceMinusFees
        );

        emit BridgedETHToL1ViaNativeBridge(l1VaultETHForL2Chain, ethBalanceMinusFees);
```

**File:** contracts/bridges/ScrollMessenger.sol (L21-24)
```text
    function sendETHToL1ViaBridge(address l2bridge, address target, uint256 value) external payable nonReentrant {
        if (msg.value != value) revert MismatchedMsgValue();
        IScrollMessenger(l2bridge).sendMessage{ value: value }(target, value, "", 0, msg.sender);
    }
```

**File:** contracts/interfaces/L2/IScrollMessenger.sol (L62-63)
```text
    /// @param gasLimit Gas limit required to complete the message relay on corresponding chain.
    function sendMessage(address target, uint256 value, bytes calldata message, uint256 gasLimit) external payable;
```

**File:** contracts/bridges/BaseMessenger.sol (L15-16)
```text
    uint32 public constant DEFAULT_GAS_LIMIT = 200_000;

```

**File:** contracts/bridges/OptimismMessenger.sol (L15-16)
```text
    /// @notice The recommended gas limit for sending ETH to L1 via the Optimism bridge
    uint32 public constant DEFAULT_GAS_LIMIT = 200_000;
```
