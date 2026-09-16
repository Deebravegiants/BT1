## Analog Found

### Title
Freezing incoming messages via `setFrozenState` also blocks timeout resolution, permanently locking escrowed funds - ([File: evm/src/core/HandlerV2.sol])

### Summary
`HandlerV2` gates every relayer-submitted message — including request delivery **and** timeout resolution — behind the same `notFrozen(host)` modifier that checks `FrozenStatus.Incoming`/`FrozenStatus.All`. This mirrors the reported pattern: an emergency "pause" mechanism blocks the recovery/closing path (`liquidate` in the reference report, `handlePostRequestTimeouts`/`handleGetRequestTimeouts` here) that is specifically meant to release user funds when the normal flow cannot complete.

### Finding Description
`HandlerV2` defines a single `notFrozen` modifier shared by every relayer entrypoint: [1](#0-0) 

This modifier is applied not only to `handlePostRequests`/`handleGetResponses` (actual new message delivery) but also to the timeout handlers that are the *only* mechanism to unwind a dispatched-but-undelivered request and refund the escrowed fee/collateral back to the sender: [2](#0-1) [3](#0-2) 

Once a relayer submits a valid timeout proof, `dispatchTimeOut`/`dispatchTimeOut` (Get) on `EvmHost` deletes the request commitment and refunds the relayer fee, and calls `onPostRequestTimeout`/`onGetRequestTimeout` on the originating app so it can release the user's locked collateral/tokens: [4](#0-3) 

The admin (or handler) can freeze the host at any time via `setFrozenState`: [5](#0-4) 

with `FrozenStatus` semantics defined as: [6](#0-5) 

Because `FrozenStatus.Incoming` (or `All`) blocks **all** `HandlerV2` entrypoints, including `handlePostRequestTimeouts` and `handleGetRequestTimeouts`, any request that is stuck (destination unavailable, censored, or simply slow) cannot be timed out and refunded while the host is frozen — exactly analogous to `liquidate` being blocked by `whenNotPaused` in the referenced report. Downstream apps such as `HyperFungibleToken`/`WrappedHyperFungibleToken` rely on `onPostRequestTimeout` to re-mint/unlock user funds after a failed cross-chain transfer: [7](#0-6) 

If the host is frozen (e.g., in response to a security incident on the destination side) while user requests are pending, those users' locked tokens cannot be recovered via timeout until the admin lifts the freeze — there is no exemption for the recovery/timeout path, unlike request delivery which can legitimately remain blocked.

### Impact Explanation
Any user with an in-flight cross-chain transfer/message (locked collateral in `HyperFungibleToken`, `WrappedHyperFungibleToken`, the LayerZero endpoint adapter, or any custom `IsmpModule` app) cannot recover funds via timeout while `FrozenStatus.Incoming`/`All` is set, even though timeout resolution is the designated safety valve for stuck messages. This causes funds to be frozen for the duration of the freeze, which — per the design — has no fixed upper bound (it persists until an admin/handler action). This matches the "permanent freezing of funds" acceptance criterion.

### Likelihood Explanation
Freezing is a normal operational lever exposed to the admin and handler for legitimate incident response (e.g., a compromised consensus client or malicious relayer on the incoming path). Any time that lever is used while requests are outstanding, affected users are unable to reclaim funds via timeout, and relayers are unable to submit the (already fee-paying) timeout proofs to unlock the standard relayer-fee refund path either. This is a reasonably likely occurrence any time a freeze is used for its intended purpose, not just a purely theoretical edge case.

### Recommendation
Introduce a separate, narrower check for timeout handlers (or a dedicated `FrozenStatus` variant) that only blocks *new* incoming request/response delivery, while still permitting `handlePostRequestTimeouts` and `handleGetRequestTimeouts` to execute so that already-dispatched, timed-out requests can always be unwound and refunded regardless of the host's frozen state — mirroring how a liquidation/close function should remain callable even when a protocol is otherwise paused.

### Proof of Concept
1. User calls `HyperFungibleToken.send()` on chain A, locking/burning tokens and dispatching a `PostRequest` with a `timeout` in the future.
2. Destination chain B experiences an incident; admin calls `EvmHost.setFrozenState(FrozenStatus.Incoming)` on chain A to halt incoming message processing.
3. The request's `timeoutTimestamp` elapses without delivery.
4. A relayer submits a non-membership proof to `HandlerV2.handlePostRequestTimeouts` on chain A to trigger the refund — the call reverts with `HostFrozen` because of the `notFrozen(host)` modifier [2](#0-1) .
5. The user's locked/burned tokens remain unrecoverable until the admin unfreezes the host, with no guaranteed timeframe.

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

**File:** evm/src/core/EvmHost.sol (L746-753)
```text
    function setFrozenState(FrozenStatus newState) external {
        address caller = _msgSender();
        if (caller != _hostParams.admin && caller != _hostParams.handler) revert UnauthorizedAction();

        _frozen = newState;

        emit HostFrozen({status: newState});
    }
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

**File:** sdk/packages/core/contracts/libraries/Message.sol (L24-33)
```text
enum FrozenStatus {
    /// @notice Normal operation - all functions are enabled
    None,
    /// @notice Incoming messages are blocked - prevents receiving cross-chain messages
    Incoming,
    /// @notice Outgoing messages are blocked - prevents sending cross-chain messages
    Outgoing,
    /// @notice All operations are frozen - complete protocol halt
    All
}
```

**File:** docs/content/developers/evm/api/hyper-fungible-token.mdx (L99-105)
```text
### onPostRequestTimeout(incoming)

Called when a sent message times out. Re-mints tokens to the original sender.

```solidity lineNumbers
function onPostRequestTimeout(PostRequestTimeout memory incoming) external onlyHost whenNotPaused
```
```
