Confirmed: `EvmHost.dispatchTimeOut(PostRequestTimeout)` at [1](#0-0)  is invoked via the permissionless `HandlerV2.handlePostRequestTimeouts` entrypoint [2](#0-1) , which calls `onPostRequestTimeout` on the source app. Both `HyperFungibleToken` and `WrappedHyperFungibleToken` gate that callback behind `whenNotPaused`.

### Title
Refund path on cross-chain send timeout is blocked by `whenNotPaused`, permanently freezing user funds while the owner pauses the token - (File: `sdk/packages/core/contracts/apps/HyperFungibleToken.sol`, `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol`)

### Summary
`HyperFungibleToken.send()` burns the caller's tokens immediately and dispatches a cross-chain POST request; `WrappedHyperFungibleToken.send()` locks the caller's ERC20/native tokens the same way. The only way to recover those funds if the message never gets delivered is the ISMP timeout callback `onPostRequestTimeout()`, which mints back (or unlocks) the funds to the original sender. Both implementations mark this callback `whenNotPaused`, so if the token is paused at any point between dispatch and timeout processing, users whose messages time out cannot recover their funds until the owner unpauses — an unprivileged relayer cannot force it through, and the user has no other recovery path.

### Finding Description
`send()` is `whenNotPaused` and burns/locks tokens before dispatch: [3](#0-2) 

The timeout refund handler is also gated by `whenNotPaused`: [4](#0-3) 

The same pattern exists in the lock/unlock wrapper, where the refund additionally has to unwrap WETH or push native ETH: [5](#0-4) 

The timeout is delivered through a fully permissionless entrypoint — anyone (a relayer, or the user themselves via self-relay) can submit the timeout proof: [2](#0-1) 

which routes to `EvmHost.dispatchTimeOut(PostRequestTimeout)`, calling `onPostRequestTimeout` on the app and only refunding relayer fees if that callback succeeds: [1](#0-0) 

If the owner pauses the token contract (e.g., for an unrelated security incident, or simply because pausing is available at any time) while a user's cross-chain send is in flight, and that message subsequently times out, the timeout callback reverts due to `whenNotPaused`. Per the host's logic, a reverting callback means the commitment is *not* deleted and the message can be resubmitted later — so the situation isn't unrecoverable forever, but it is entirely dependent on the owner unpausing, with no way for the user or relayer to force recovery of already-burned/locked funds while paused. This mirrors the reported pattern: pausing legitimately stops new risky operations (`send`, `onAccept`) but should not also block users from getting back funds they already committed.

### Impact Explanation
Users who dispatched a cross-chain transfer that times out cannot reclaim their burned/locked tokens for as long as the contract stays paused. Since pausing is entirely at the owner's discretion and duration, and there is no guarantee (or on-chain mechanism enforcing) a bounded pause window, this constitutes user funds being frozen contingent on admin action rather than being recoverable unilaterally by the affected user or relayer — a classic griefing/DoS-on-withdrawal condition that the analog report flags as a Medium-severity issue.

### Likelihood Explanation
Likelihood is moderate: it requires (1) a user dispatching `send()`, (2) the message timing out (network delay, unresponsive relayers, or destination chain issues), and (3) the owner pausing the contract in that window (for any reason, including legitimate emergency response unrelated to this specific transfer). Given pause is a normal operational lever exposed to a single owner key, and cross-chain timeouts are a routine occurrence in bridging, this scenario is realistic to occur, especially since the owner pausing to react to one incident would incidentally block unrelated users' timeout refunds.

### Recommendation
Remove the `whenNotPaused` modifier from `onPostRequestTimeout` (and `onGetTimeout`, if similarly gated) in `HyperFungibleToken`, `HyperFungibleTokenUpgradeable`, `WrappedHyperFungibleToken`, and `WrappedHyperFungibleTokenUpgradeable`, so refunds for already-committed funds remain processable regardless of pause state. Pausing should continue to block new `send()`/`onAccept()` operations that create new exposure, but not exit paths for funds already at risk.

### Proof of Concept
1. User calls `HyperFungibleToken.send()` with `amount = X`; `X` tokens are burned from the user and a POST request is dispatched cross-chain.
2. Before the request is delivered, the contract owner calls `pause()` (for any reason).
3. The request exceeds its `timeout` on the destination chain without being delivered (network conditions, relayer downtime, etc.).
4. Anyone submits `HandlerV2.handlePostRequestTimeouts` with a valid non-membership proof; `EvmHost.dispatchTimeOut` calls `onPostRequestTimeout` on the token contract.
5. The call reverts because of `whenNotPaused`, so `X` tokens remain unrecoverable by the user until the owner calls `unpause()` — the user has no independent means to reclaim their burned tokens in the interim.

### Citations

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

**File:** evm/src/core/HandlerV2.sol (L254-286)
```text
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
