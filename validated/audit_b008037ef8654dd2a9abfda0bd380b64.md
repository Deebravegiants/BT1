## Title
`HandlerV2.notFrozen` blocks processing of already-timed-out requests, permanently stranding burned/locked bridge principal — ([File: evm/src/core/HandlerV2.sol])

### Summary
The `notFrozen(host)` modifier applied to `HandlerV2.handlePostRequestTimeouts` (and `handleGetRequestTimeouts`) reverts with `HostFrozen()` whenever the host's `FrozenStatus` is `Incoming` or `All` [1](#0-0) . This blocks the *timeout-recovery* path, not just new incoming message delivery. Any user who has already burned tokens in `HyperFungibleToken.send()` or locked tokens in `WrappedHyperFungibleToken.send()` and whose cross-chain POST request subsequently times out cannot have that timeout processed — and therefore cannot be refunded via `onPostRequestTimeout` — for as long as the host remains frozen in `Incoming`/`All` mode. This is the same bug class as the H-04 report: an emergency/mode guard is applied indiscriminately to a step that is supposed to let users reclaim funds that are already committed, rather than only to the creation of new, potentially unsafe state.

### Finding Description
`EvmHost.setFrozenState()` lets the admin or handler set the host to `Incoming`, `Outgoing`, or `All` in response to a security incident (e.g. a suspected byzantine consensus update) [2](#0-1) . The intent, per the docs, is to halt specific protocol operations during security incidents [3](#0-2) .

However, `HandlerV2.notFrozen` gates *all* incoming-message handlers — including `handlePostRequestTimeouts`, which is the permissionless mechanism relayers use to deliver a non-membership proof that a POST request was never received on the destination, triggering the source application's `onPostRequestTimeout()` refund callback: [4](#0-3) 

While the host is frozen with `Incoming` or `All`, this function unconditionally reverts, so `EvmHost.dispatchTimeOut(PostRequestTimeout, ...)` and the downstream `onPostRequestTimeout` on the token app can never be reached: [5](#0-4) 

Meanwhile, `HyperFungibleToken.onPostRequestTimeout` is the only path that re-mints previously burned tokens back to the sender, and `WrappedHyperFungibleToken.onPostRequestTimeout` is the only path that releases previously locked underlying tokens: [6](#0-5) [7](#0-6) 

Tokens are burned/locked at `send()` time, *before* the message is ever delivered or times out [8](#0-7) . Once a request has timed out, the user's only recourse is the timeout-refund flow — exactly the "approved withdrawal, final step to finalize" scenario described in the H-04 report. By gating this recovery step behind `notFrozen`, the protocol reproduces the same defect: an emergency mode designed to stop *new* unsafe deliveries also blocks the *finalization of funds that are already committed and awaiting recovery*, with no alternate recovery path once frozen.

### Impact Explanation
Any relayer or user attempting to process a timed-out POST request while the host is frozen (`Incoming` or `All`) will have every `handlePostRequestTimeouts` call revert with `HostFrozen()`. For the duration of the freeze, all pending timed-out transfers through `HyperFungibleToken`/`WrappedHyperFungibleToken` (and any other `IApp` relying on `onPostRequestTimeout` for refunds) are unrecoverable — burned tokens cannot be re-minted and locked underlying tokens cannot be released, even though the tokens are already gone from circulation on the source side. This is high impact: user principal becomes stuck with no available on-chain action, mirroring "tokens stuck" in the original report.

### Likelihood Explanation
Medium: it requires (a) the host being placed into `Incoming`/`All` frozen state (an expected operational response to a detected consensus/security issue) and (b) pending outbound requests that time out during that window. Both conditions are realistic — freezing is the documented incident-response mechanism, and any active bridge will have in-flight transfers when an incident occurs.

### Recommendation
Do not gate `handlePostRequestTimeouts` (and `handleGetRequestTimeouts`) behind `notFrozen` when the frozen status is `Incoming`. Timeout processing only requires the state machine's stored commitment and a non-membership proof already verified by consensus checks made *before* the incident triggered the freeze; it does not admit new, unverified consensus/state updates. At minimum, distinguish "freeze new consensus/state updates" from "freeze processing of already-known commitments," and allow the latter (timeout finalization/refunds) to proceed so committed user funds remain recoverable regardless of frozen status.

### Proof of Concept
1. User calls `HyperFungibleToken.send()`, burning `amount` tokens and dispatching a POST request with `timeout = T`.
2. Before delivery, the admin detects a security issue and calls `EvmHost.setFrozenState(FrozenStatus.Incoming)`.
3. Time passes beyond `T`; the request times out without being delivered.
4. A relayer submits `HandlerV2.handlePostRequestTimeouts(host, message)` with a valid non-membership proof.
5. The call reverts with `HostFrozen()` due to the `notFrozen(host)` modifier [1](#0-0) , so `onPostRequestTimeout` is never invoked and the user's burned tokens are never re-minted, for as long as the freeze remains active.

### Citations

**File:** evm/src/core/HandlerV2.sol (L106-112)
```text
     * @dev Checks if the host permits incoming datagrams
     */
    modifier notFrozen(IHost host) {
        FrozenStatus state = host.frozen();
        if (state == FrozenStatus.Incoming || state == FrozenStatus.All) revert HostFrozen();
        _;
    }
```

**File:** evm/src/core/HandlerV2.sol (L249-286)
```text
    /**
     * @dev Checks the provided timed-out requests and their proofs, before dispatching them to their relevant destination modules
     * @param host - IsmpHost
     * @param message - batch post request timeouts
     */
    function handlePostRequestTimeouts(IHost host, PostRequestTimeoutMessage calldata message)
        external
        notFrozen(host)
    {
        uint256 delay = block.timestamp - host.stateMachineCommitmentUpdateTime(message.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

        // fetch the state commitment
        StateCommitment memory state = host.stateMachineCommitment(message.height);
        if (state.stateRoot == bytes32(0)) revert StateCommitmentNotFound();
        uint256 timeoutsLength = message.timeouts.length;

        for (uint256 i = 0; i < timeoutsLength; ++i) {
            PostRequest memory request = message.timeouts[i];
            // timed-out?
            if (request.timeout() > state.timestamp) revert MessageNotTimedOut();

            // known request? also serves as source check
            bytes32 requestCommitment = request.hash();
            FeeMetadata memory meta = host.requestCommitments(requestCommitment);
            if (meta.sender == address(0)) revert UnknownMessage();

            bytes[] memory keys = new bytes[](1);
            keys[0] = bytes.concat(REQUEST_RECEIPTS_STORAGE_PREFIX, requestCommitment);

            // verify state trie non-membership proofs
            PolkadotTrie.StorageValue memory entry = PolkadotTrie.VerifyProof(state.stateRoot, message.proof, keys)[0];
            if (entry.value.length != 0) revert InvalidProof();

            host.dispatchTimeOut(PostRequestTimeout(request, _msgSender()), meta, requestCommitment);
        }
    }
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

**File:** sdk/packages/core/contracts/libraries/Message.sol (L19-33)
```text
/**
 * @title FrozenStatus
 * @notice Represents the frozen state of the Host for security and emergency situations
 * @dev Used to halt specific protocol operations during security incidents or upgrades
 */
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

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L264-282)
```text
    function send(SendParams calldata params) external payable whenNotPaused {
        _burn(msg.sender, params.amount);
        DispatchPost memory request = _buildDispatchPost(params);

        bytes32 commitment;
        if (msg.value > 0) {
            commitment = IDispatcher(_host).dispatch{value: msg.value}(request);
        } else {
            commitment = dispatchWithFeeToken(request);
        }

        emit Sent({
            from: msg.sender,
            to: params.to,
            dest: string(params.dest),
            amount: params.amount,
            commitment: commitment
        });
    }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L315-326)
```text
    /**
     * @notice Handles timeout of a previously dispatched cross-chain transfer
     * @dev Called by the ISMP host when a sent message times out without being delivered.
     * Re-mints the burned tokens back to the original sender as a refund.
     * @param incoming The timed-out POST request and the relayer that submitted the timeout proof
     */
    function onPostRequestTimeout(PostRequestTimeout memory incoming) public virtual override onlyHost whenNotPaused {
        Message memory message = abi.decode(incoming.request.body, (Message));
        address refundee = _toAddr(message.from);
        _mint(refundee, message.amount);
        emit Refunded({to: refundee, amount: message.amount});
    }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L338-365)
```text
    /**
     * @notice Handles timeout of a previously dispatched cross-chain transfer
     * @dev Called by the ISMP host when a sent message times out without being delivered.
     * Attempts to unwrap WETH and refund native tokens.
     * @param incoming The timed-out POST request and the relayer that submitted the timeout proof
     */
    function onPostRequestTimeout(PostRequestTimeout calldata incoming) external override onlyHost whenNotPaused {
        HyperFungibleToken.Message memory message = abi.decode(incoming.request.body, (HyperFungibleToken.Message));
        address refundee = _toAddr(message.from);

        if (_isWeth) {
            // Try a native-ETH push first; if the refundee cannot accept native value
            // (e.g. the caller used the ERC-20 deposit path in `send()` from a
            // non-payable contract), re-wrap the withdrawn ETH and deliver the
            // underlying WETH as an ERC-20 transfer so the timeout still settles and
            // funds are not permanently locked.
            IWETH(_underlying).withdraw(message.amount);
            (bool sent,) = refundee.call{value: message.amount}("");
            if (!sent) {
                IWETH(_underlying).deposit{value: message.amount}();
                IERC20(_underlying).safeTransfer(refundee, message.amount);
            }
        } else {
            IERC20(_underlying).safeTransfer(refundee, message.amount);
        }

        emit Refunded({to: refundee, amount: message.amount});
    }
```
