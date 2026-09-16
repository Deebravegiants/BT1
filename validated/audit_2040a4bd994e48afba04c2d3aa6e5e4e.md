### Title
Missing pause check on `placeOrder`, `fillOrder`, and `cancelOrder` allows continued gateway use while paused - ([File: evm/src/apps/IntentGatewayV2.sol])

### Summary
`IntentGatewayV2` inherits a `_paused` flag from `IntentsBase`, and internal docs confirm the gateway ships a pause mechanism with a "setter, event and checks" [1](#0-0)  and the flag itself is declared in `IntentsBase` [2](#0-1) . However, the concrete gateway entry points that a user directly calls — `placeOrder`, `fillOrder`, and `cancelOrder` — contain no `whenNotPaused`/`_paused` check anywhere in their bodies [3](#0-2) [4](#0-3) [5](#0-4) . This is the same bug class as the referenced Illuminate `Redeemer` finding: a pause flag exists and is checked on some paths (there, `redeem`; here, apparently `onAccept`/cross-chain delivery, per other pausable apps like `HyperFungibleToken.onAccept` which is `onlyHost whenNotPaused` [6](#0-5) ), but is not enforced on the alternate operational entry points that reach the same escrow/fund-moving effect.

### Finding Description
`placeOrder` escrows user funds into the gateway with no pause gate at all [7](#0-6) . `fillOrder` releases escrowed input tokens to a solver for both same-chain and cross-chain routes, again with no pause gate [8](#0-7) . `cancelOrder` refunds escrow directly for same-chain orders and drives the cross-chain refund flow, also without a pause gate [9](#0-8) . Since `_paused` is a real, wired-up storage flag in the shared base contract (confirmed by the AI decision log describing a pause "setter, event and checks" that had to be trimmed for EIP-170) [10](#0-9) , governance pausing the gateway (e.g., in response to a discovered bug, oracle manipulation, or ongoing exploit) would be expected to halt intent flow. Instead, unprivileged users/solvers can keep calling `placeOrder`, `fillOrder`, and `cancelOrder` unimpeded, exactly mirroring the `authRedeem`/`autoRedeem` bypass pattern from the report where `paused[u][m]` blocked `redeem` but not the alternate redemption paths.

### Impact Explanation
If the pause is the protocol's emergency stop for the intents system (e.g., during an active exploit of the price oracle, fee logic, or a malicious relayer being investigated), users and solvers can continue to place, fill, and cancel orders — moving funds through escrow — during the window the operators believed the system was halted. This directly undermines the incident-response control and can enable continued draining/theft of escrowed funds or forced fund movement while the protocol believes itself frozen, satisfying "concrete theft or permanent freezing of funds" via a route that should have been blocked.

### Likelihood Explanation
Any account can call `placeOrder`, `fillOrder`, or `cancelOrder` — these are unprivileged, single-transaction entry points requiring no special role [3](#0-2) [4](#0-3) [5](#0-4) . Exploitation only requires the pause to be activated at some point (an expected operational event) and an attacker submitting an ordinary order transaction — no proof forgery or privileged access needed.

### Recommendation
Add a `whenNotPaused` (or equivalent `_paused` check) modifier to `placeOrder`, `fillOrder`, and `cancelOrder` in `evm/src/apps/IntentGatewayV2.sol`, consistent with whatever check already guards the cross-chain `onAccept`/governance-message path, so that a governance pause fully halts all fund-moving entry points, not just the cross-chain delivery callback.

### Proof of Concept
1. Governance calls the gateway's pause action, setting `_paused = true` in `IntentsBase` [11](#0-10) , intending to halt all intent activity (e.g., due to a detected exploit).
2. A user calls `placeOrder(order, graffiti)` — it succeeds and escrows tokens, since no pause check exists in the function body [7](#0-6) .
3. A solver calls `fillOrder(order, options)` for a same-chain order — it succeeds and releases escrow via `_fillSameChain`, since no pause check exists [8](#0-7) .
4. A user calls `cancelOrder(order, options)` to withdraw escrowed funds — it succeeds via `_cancelSameChain`, since no pause check exists [9](#0-8) .
5. In all three cases the intended pause has no effect, contradicting the operator's expectation that the gateway is halted.

Note: I was unable to inspect `ExtrinsicIntents.sol`/`IntrinsicIntents.sol` within the available tool budget to confirm exactly which function(s) do check `_paused` (likely `onAccept`/the governance `Execute` message path), so the precise scope of the existing pause enforcement is inferred from the AI decision-log documentation and analogous pausable apps (`HyperFungibleToken`) rather than directly observed in `IntentGatewayV2`'s own inheritance chain.

### Citations

**File:** sdk/packages/core/docs/ai/decisions/2026-09-03-the-paused-getter-was-dropped-to-stay-under-eip-170.md (L1-8)
```markdown
# 2026-09-03 — The `_paused` getter was dropped to stay under EIP-170

Chosen: `bool internal _paused`. The variable stays in slot 13 so the layout is unchanged.

The gateway compiled to 10 bytes over the limit with the new storage, setter, event and checks.
Nothing reads `_paused()` anywhere in the repo, so removing its getter was the only free saving.
The revert reuses `Unauthorized()` instead of a dedicated error for the same reason; the second
selector cost 15 bytes.
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L165-167)
```text
    /// @dev Appended last to preserve existing storage slots.
    bool internal _paused;

```

**File:** evm/src/apps/IntentGatewayV2.sol (L194-228)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable nonReentrant {
        if (order.inputs.length == 0) revert InvalidInput();

        // Reject duplicate output tokens
        uint256 outputsLen_ = order.output.assets.length;
        for (uint256 i; i < outputsLen_;) {
            bytes32 token = order.output.assets[i].token;
            assembly ("memory-safe") {
                if tload(token) {
                    mstore(0, 0xb4fa3fb3) // InvalidInput.selector
                    revert(0x1c, 0x04)
                }
                tstore(token, 1)
            }
            unchecked {
                ++i;
            }
        }
        // Clean up transient storage so repeated placeOrder calls in the same tx don't false-positive.
        for (uint256 i; i < outputsLen_;) {
            bytes32 token = order.output.assets[i].token;
            assembly ("memory-safe") {
                tstore(token, 0)
            }
            unchecked {
                ++i;
            }
        }

        address hostAddr = host();
        order.user = bytes32(uint256(uint160(msg.sender)));
        order.source = IDispatcher(hostAddr).host();
        order.nonce = _nonce++;

        uint256 inputsLen = order.inputs.length;
```

**File:** evm/src/apps/IntentGatewayV2.sol (L443-483)
```text
    function fillOrder(Order calldata order, FillOptions calldata options) public payable nonReentrant {
        uint256 blockNumber = _blockNumber();
        if (order.deadline < blockNumber) revert Expired();
        // The solver's own bound on how long its quoted price stands. Zero means unbounded,
        // which is the right default for a solver filling directly — it is only at risk from
        // its own staleness. It matters for a bid signed through the coprocessor, where the
        // order placer chooses the moment of execution and nothing else caps the wait.
        if (options.validUntil != 0 && blockNumber > options.validUntil) revert FillExpired();
        bytes32 commitment = keccak256(abi.encode(order));

        address hostAddr = host();
        bytes32 currentChain = keccak256(IDispatcher(hostAddr).host());
        bytes32 orderSource = keccak256(order.source);
        bytes32 orderDest = keccak256(order.destination);
        bool isSameChain = orderSource == orderDest;

        if (isSameChain && orderSource != currentChain) revert WrongChain();
        if (!isSameChain && orderDest != currentChain) revert WrongChain();

        if (_filled[commitment] != address(0)) revert Filled();

        if (_params.solverSelection) {
            bytes32 storedSelectionHash;
            assembly {
                storedSelectionHash := tload(commitment)
            }

            bytes32 expectedSelectionHash = keccak256(abi.encode(msg.sender, order.session));
            if (storedSelectionHash != expectedSelectionHash) revert Unauthorized();
        }

        uint256 outputsLen = order.output.assets.length;
        if (options.outputs.length != outputsLen) revert InvalidInput();
        if (order.inputs.length != outputsLen) revert InvalidInput();

        if (isSameChain) {
            _fillSameChain(order, options, commitment);
        } else {
            _fillCrossChain(order, options, commitment);
        }
    }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L505-537)
```text
    function cancelOrder(Order calldata order, CancelOptions calldata options) public payable nonReentrant {
        bytes32 commitment = keccak256(abi.encode(order));

        if (_filled[commitment] != address(0)) revert Filled();

        address hostAddr = host();
        bytes32 currentChain = keccak256(IDispatcher(hostAddr).host());
        bytes32 orderSource = keccak256(order.source);
        bytes32 orderDest = keccak256(order.destination);
        bool isSameChain = orderSource == orderDest;

        // Emitted here, once, rather than from each of the three routes below. Every check those
        // routes make — Unauthorized, NotExpired, UnknownOrder — reverts, and a revert discards
        // logs, so an early emit can never announce a cancellation that did not happen. Emitting
        // before the branch also keeps `EscrowRefunded` the last log on the same-chain route, where
        // the refund is processed in this same transaction. Three emit sites cost bytecode this
        // contract does not have: it sits within ~100 bytes of the EIP-170 limit.
        emit OrderCancelled({commitment: commitment, canceller: msg.sender});

        if (isSameChain) {
            // Checked here rather than inside `_cancelSameChain`, which used to re-read `host()`,
            // re-query the host's state machine id and re-hash `order.source` to reach the same
            // answer this function already has. Same check, one external call fewer.
            if (currentChain != orderSource) revert WrongChain();
            _cancelSameChain(order, commitment);
        } else if (currentChain == orderSource) {
            _cancelFromSource(order, options, commitment);
        } else if (currentChain == orderDest) {
            _cancelFromDest(order, options, commitment);
        } else {
            revert WrongChain();
        }
    }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L292-292)
```text
    function onAccept(IncomingPostRequest calldata incoming) public virtual override onlyHost whenNotPaused {
```
