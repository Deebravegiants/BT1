### Title
Timeout Handlers Unnecessarily Gated on `Incoming`-Freeze, Blocking Refund/Recovery Path When It Is Needed Most - (File: evm/src/core/HandlerV2.sol)

### Summary
`HandlerV2.handlePostRequestTimeouts` and `HandlerV2.handleGetRequestTimeouts` are both gated by the `notFrozen(host)` modifier, which reverts with `HostFrozen()` whenever the host's `FrozenStatus` is `Incoming` or `All` [1](#0-0) . This is the same class of bug as the LooksRare report: a check that exists to gate one class of action (delivery of new *incoming* messages) is reused, without justification, on a distinct recovery/settlement function (processing *timeouts* of previously-sent *outgoing* requests) that should not be subject to that same restriction.

### Finding Description
`notFrozen(host)` is documented as a check for "if the host permits incoming datagrams" [2](#0-1) . It is correctly applied to `handlePostRequests` and `handleGetResponses`, which deliver new incoming cross-chain messages to local applications [3](#0-2) [4](#0-3) .

However, the same modifier is also applied to `handlePostRequestTimeouts` and `handleGetRequestTimeouts` [5](#0-4) [6](#0-5) . These functions do not deliver new incoming messages — they process the timeout of requests that were previously *sent* from this chain and never delivered, verifying a non-membership proof and then calling `host.dispatchTimeOut(...)`, which invokes the source application's `onPostRequestTimeout`/`onGetTimeout` callback and refunds the relayer fee [7](#0-6) . In apps like the intent gateways, this timeout path is the mechanism that un-escrows or refunds user funds when a cross-chain message cannot be delivered (e.g., `onPostRequestTimeout` in `HyperFungibleTokenUpgradeable.sol` re-mints burned tokens back to the sender) [8](#0-7) .

Because `notFrozen` treats `FrozenStatus.Incoming` the same as `FrozenStatus.All`, freezing only incoming message delivery (e.g., in response to a consensus fault or malicious relaying of incoming datagrams) also blocks users from recovering funds via the timeout/refund path — even though timeout processing has nothing to do with accepting new incoming datagrams and does not expose the same risk the freeze was meant to mitigate.

### Impact Explanation
If the host is put into `FrozenStatus.Incoming` (a state explicitly distinct from `All`, implying the admin/governance intended to still allow some other class of operation while blocking incoming delivery), all pending outgoing requests that would otherwise time out and refund/un-escrow user or protocol funds become permanently stuck for the duration of the freeze. This is a denial of legitimate recovery exactly analogous to the reported issue: an outflow/behavior-gating check applied to state-recovery functions prevents users from reclaiming funds precisely when the system is already in a degraded state and such recovery is most needed. Depending on how long `Incoming` freeze is held (there is no expiry visible in the reviewed code), this can amount to prolonged or indefinite freezing of user funds that are only recoverable through the timeout path.

### Likelihood Explanation
This path is reachable by any relayer submitting a legitimate, well-formed timeout message via `handlePostRequestTimeouts`/`handleGetRequestTimeouts` — a permissionless, unprivileged action — as soon as the host is set to `FrozenStatus.Incoming`. No malicious relayer or governance action is required to trigger the block; it occurs automatically as a side effect of a state that is supposed to only restrict incoming delivery.

### Recommendation
Split the freeze check so that timeout-processing functions are gated only on `FrozenStatus.All` (or a dedicated status), not `FrozenStatus.Incoming`, since timeout processing is a recovery/refund mechanism for outgoing requests, not incoming-message delivery. Concretely, introduce a distinct modifier for timeout handlers (or check `host.frozen() == FrozenStatus.All` directly) in `handlePostRequestTimeouts` and `handleGetRequestTimeouts`, leaving `notFrozen` (`Incoming`/`All`) only on `handlePostRequests` and `handleGetResponses`.

### Proof of Concept
1. Host admin/governance calls whatever function sets `_frozen = FrozenStatus.Incoming` (intended to stop new incoming message delivery only, e.g. during a consensus incident).
2. A user's previously-dispatched `PostRequest` (e.g. an Intent Gateway cross-chain order, or a `HyperFungibleTokenUpgradeable` transfer) has already timed out on the destination and its refund is due via `onPostRequestTimeout`.
3. A relayer submits a valid `PostRequestTimeoutMessage` with a correct non-membership proof to `HandlerV2.handlePostRequestTimeouts`.
4. The call reverts with `HostFrozen()` because of the `notFrozen(host)` modifier check against `FrozenStatus.Incoming` [5](#0-4) , even though the timeout has nothing to do with incoming datagram delivery.
5. The user's escrowed/burned funds remain locked and cannot be refunded until the admin lifts the `Incoming` freeze, even though the freeze was never meant to block outgoing-request recovery.

Note: I was unable to locate the exact admin function/entrypoint that sets `_frozen` to `FrozenStatus.Incoming` versus `All` within the indexed portion of `EvmHost.sol` (the enum declaration and setter are defined in `sdk/packages/core/contracts/interfaces/IHost.sol` and possibly `evm/src/core/EvmHost.sol`, but their full bodies were not returned by the index). A Devin session with full repository access would be needed to confirm the exact semantics/duration of `FrozenStatus.Incoming` versus `All` and how it is set, to fully validate the intended scope of the freeze and finalize the fix.

### Citations

**File:** evm/src/core/HandlerV2.sol (L105-112)
```text
    /**
     * @dev Checks if the host permits incoming datagrams
     */
    modifier notFrozen(IHost host) {
        FrozenStatus state = host.frozen();
        if (state == FrozenStatus.Incoming || state == FrozenStatus.All) revert HostFrozen();
        _;
    }
```

**File:** evm/src/core/HandlerV2.sol (L181-210)
```text
    function handlePostRequests(IHost host, PostRequestMessage calldata request) external notFrozen(host) {
        uint256 timestamp = block.timestamp;
        uint256 delay = timestamp - host.stateMachineCommitmentUpdateTime(request.proof.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

        uint256 requestsLen = request.requests.length;
        MerkleMountainRange.Leaf[] memory leaves = new MerkleMountainRange.Leaf[](requestsLen);

        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // check destination
            if (!leaf.request.dest.equals(host.host())) revert InvalidMessageDestination();
            // check time-out
            if (timestamp >= leaf.request.timeout()) revert MessageTimedOut();
            leaves[i] = MerkleMountainRange.Leaf(leaf.index, leaf.request.hash());
        }

        bytes32 root = host.stateMachineCommitment(request.proof.height).overlayRoot;
        if (root == bytes32(0)) revert StateCommitmentNotFound();
        bool valid = MerkleMountainRange.VerifyProof(root, request.proof.multiproof, leaves, request.proof.leafCount);
        if (!valid) revert InvalidProof();

        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // duplicate request?
            if (host.requestReceipts(leaf.request.hash()) != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.request, _msgSender());
        }
    }
```

**File:** evm/src/core/HandlerV2.sol (L217-247)
```text
    function handleGetResponses(IHost host, GetResponseMessage calldata message) external notFrozen(host) {
        uint256 timestamp = block.timestamp;
        uint256 delay = timestamp - host.stateMachineCommitmentUpdateTime(message.proof.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

        uint256 responsesLength = message.responses.length;
        MerkleMountainRange.Leaf[] memory leaves = new MerkleMountainRange.Leaf[](responsesLength);

        for (uint256 i = 0; i < responsesLength; ++i) {
            GetResponseLeaf memory leaf = message.responses[i];
            // don't check for timeouts because it's checked on Hyperbridge

            // known request? also serves as source check
            FeeMetadata memory meta = host.requestCommitments(leaf.response.request.hash());
            if (meta.sender == address(0)) revert UnknownMessage();
            leaves[i] = MerkleMountainRange.Leaf(leaf.index, leaf.response.hash());
        }

        bytes32 root = host.stateMachineCommitment(message.proof.height).overlayRoot;
        if (root == bytes32(0)) revert StateCommitmentNotFound();
        bool valid = MerkleMountainRange.VerifyProof(root, message.proof.multiproof, leaves, message.proof.leafCount);
        if (!valid) revert InvalidProof();

        for (uint256 i = 0; i < responsesLength; ++i) {
            GetResponseLeaf memory leaf = message.responses[i];
            // duplicate response?
            if (host.responseReceipts(leaf.response.request.hash()).relayer != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.response, _msgSender());
        }
    }
```

**File:** evm/src/core/HandlerV2.sol (L254-260)
```text
    function handlePostRequestTimeouts(IHost host, PostRequestTimeoutMessage calldata message)
        external
        notFrozen(host)
    {
        uint256 delay = block.timestamp - host.stateMachineCommitmentUpdateTime(message.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();
```

**File:** evm/src/core/HandlerV2.sol (L293-296)
```text
    function handleGetRequestTimeouts(IHost host, GetTimeoutMessage calldata message) external notFrozen(host) {
        uint256 delay = block.timestamp - host.stateMachineCommitmentUpdateTime(message.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();
```

**File:** evm/src/core/EvmHost.sol (L885-906)
```text
    function dispatchTimeOut(
        PostRequestTimeout memory timeout,
        FeeMetadata memory meta,
        bytes32 commitment
    ) external restrict(_hostParams.handler) {
        // replay protection
        delete _requestCommitments[commitment];
        (bool success,) = _bytesToAddress(timeout.request.from)
            .call(abi.encodeWithSelector(IApp.onPostRequestTimeout.selector, timeout));

        if (!success) {
            // so that it can be retried
            _requestCommitments[commitment] = meta;
            return;
        }

        if (meta.fee != 0) {
            // refund relayer fee
            IERC20(feeToken()).safeTransfer(meta.sender, meta.fee);
        }
        emit PostRequestTimeoutHandled({commitment: commitment, dest: string(timeout.request.dest)});
    }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol (L338-349)
```text
    /**
     * @notice Handles timeout of a previously dispatched cross-chain transfer
     * @dev Called by the ISMP host when a sent message times out without being delivered.
     * Re-mints the burned tokens back to the original sender as a refund.
     * @param incoming The timed-out POST request and the relayer that submitted the timeout proof
     */
    function onPostRequestTimeout(PostRequestTimeout memory incoming) external override onlyHost whenNotPaused {
        Message memory message = abi.decode(incoming.request.body, (Message));
        address refundee = _toAddr(message.from);
        _mint(refundee, message.amount);
        emit Refunded({to: refundee, amount: message.amount});
    }
```
