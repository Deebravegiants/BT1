### Title
Stale L2 Receiver in In-Flight CCIP Messages Due to Unguarded `setL2Receiver` Update — (`contracts/L1VaultV2.sol`)

---

### Summary

`bridgeRsETHToL2UsingCCIP` encodes the current `l2Receiver` into the CCIP message at call time. A subsequent `setL2Receiver` call by a `TIMELOCK_ROLE` actor updates only the storage variable and has no effect on already-submitted messages. Any CCIP message in-flight at the time of the update will be delivered to the old receiver address, which may no longer be able to distribute yield.

---

### Finding Description

In `contracts/L1VaultV2.sol`, `bridgeRsETHToL2UsingCCIP` constructs the CCIP message by calling `getCCIPMessage`, which reads `l2Receiver` via `getReceiver()` and encodes it as the `receiver` field: [1](#0-0) 

Once `ccipSend` is called, the receiver address is immutably committed inside the CCIP protocol: [2](#0-1) 

`setL2Receiver` is callable by any `TIMELOCK_ROLE` holder with no guard against in-flight messages: [3](#0-2) 

There is no nonce, pending-message counter, or lock that would prevent `setL2Receiver` from executing while a CCIP message is in transit. The two operations are fully independent.

---

### Impact Explanation

rsETH tokens delivered to the old `l2Receiver` are permanently stranded there if that contract has been deprecated (e.g., its `MINTER_ROLE` revoked, paused, or replaced). Users on L2 whose yield depends on the new receiver never receive those tokens. The loss is permanent because CCIP messages cannot be recalled or redirected after `ccipSend` returns.

**Impact: Medium — Permanent freezing of unclaimed yield.**

---

### Likelihood Explanation

The scenario is realistic in normal operations:

1. `MANAGER_ROLE` calls `bridgeRsETHToL2UsingCCIP`. CCIP delivery takes minutes to hours.
2. Governance schedules a `setL2Receiver` update via the timelock (e.g., to migrate to a new wrapper contract).
3. The timelock delay expires and `setL2Receiver` executes while the CCIP message is still in-flight.
4. CCIP delivers rsETH to the old, now-deprecated wrapper.

Neither actor is acting maliciously; both are performing legitimate operations. The contract provides no mechanism to detect or prevent the overlap.

---

### Recommendation

Before allowing `setL2Receiver` to execute, require that no CCIP messages are in-flight. One approach:

- Maintain a counter `pendingCCIPMessages` incremented in `bridgeRsETHToL2UsingCCIP` and decremented in a `ccipReceive` acknowledgement or a manual confirmation function.
- Add `require(pendingCCIPMessages == 0, "messages in flight")` to `setL2Receiver`.

Alternatively, emit the receiver address as part of the CCIP message `data` field so the L2 side can validate it matches the expected current receiver, and revert/refund if it does not.

---

### Proof of Concept

```
// Fork-safe sequence (Foundry):
// 1. Deploy L1VaultV2 with bridgeType = CCIP, l2Receiver = oldReceiver.
// 2. MANAGER_ROLE calls bridgeRsETHToL2UsingCCIP(amount).
//    → CCIP message committed with receiver = oldReceiver.
// 3. TIMELOCK_ROLE calls setL2Receiver(newReceiver).
//    → l2Receiver storage updated; in-flight message unaffected.
// 4. Simulate CCIP delivery to oldReceiver (mock ccipRouter callback).
//    → rsETH minted/transferred at oldReceiver.
// 5. Assert: oldReceiver holds rsETH but newReceiver holds 0.
//    Assert: if oldReceiver.MINTER_ROLE is revoked, rsETH is permanently frozen.
```

The root cause is the absence of any coordination between `setL2Receiver` and `bridgeRsETHToL2UsingCCIP`: [4](#0-3) [3](#0-2)

### Citations

**File:** contracts/L1VaultV2.sol (L341-367)
```text
    function bridgeRsETHToL2UsingCCIP(uint256 amount) external payable nonReentrant onlyRole(MANAGER_ROLE) {
        if (bridgeType != BridgeType.CCIP) {
            revert InactiveBridgeType();
        }

        if (rsETH.balanceOf(address(this)) < amount) {
            revert InsufficientRsETHBalance();
        }

        if (amount == 0) {
            revert ZeroAmount();
        }

        uint256 fee = getCCIPFee(amount);

        if (msg.value != fee) {
            revert IncorrectCCIPFee();
        }

        IERC20(address(rsETH)).safeIncreaseAllowance(address(ccipRouter), amount);

        Client.EVM2AnyMessage memory message = getCCIPMessage(amount);

        bytes32 messageId = ccipRouter.ccipSend{ value: msg.value }(destinationChainSelector, message);

        emit BridgedRsETHToL2UsingCCIP(destinationChainSelector, l2Receiver, amount, messageId);
    }
```

**File:** contracts/L1VaultV2.sol (L425-427)
```text
        return Client.EVM2AnyMessage({
            receiver: abi.encodePacked(getReceiver()),
            data: bytes(""),
```

**File:** contracts/L1VaultV2.sol (L488-492)
```text
    function setL2Receiver(address _l2Receiver) external onlyRole(TIMELOCK_ROLE) {
        UtilLib.checkNonZeroAddress(_l2Receiver);
        l2Receiver = _l2Receiver;
        emit L2ReceiverSet(_l2Receiver);
    }
```
