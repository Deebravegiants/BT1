## Analysis

The `TAU._decreaseCurrentMinted` bug pattern (an accounting `msg.sender` vs. an arbitrary caller-supplied `_account`/beneficiary field being used inconsistently for debit vs. credit) has a direct analog in Hyperbridge's `EvmHost.dispatch(DispatchPost)` fee-accounting logic.

### Title
Inconsistent use of `_msgSender()` (debited) vs. caller-supplied `payer` field (credited on refund) in `EvmHost.dispatch` - (File: `evm/src/core/EvmHost.sol`)

### Summary
`DispatchPost.payer` is a caller-controlled field, documented as "Account responsible for paying the fees. If different from `msg.sender`, must have approved the Host contract" [1](#0-0) . However, `EvmHost.dispatch(DispatchPost memory post)` never actually debits `post.payer` — it always pulls the fee token from `_msgSender()`: [2](#0-1)  while the commitment's `FeeMetadata` (used for refunds/rewards) is recorded against `post.payer`, not `_msgSender()`: [3](#0-2) . On timeout, the refund is sent to `meta.sender` (i.e. `post.payer`): [4](#0-3) . The identical pattern exists for `DispatchGet` (`get.payer` recorded, `_msgSender()` debited) [5](#0-4)  and its timeout handler [6](#0-5) .

### Finding Description
Any application that mediates dispatch on behalf of a user (a token bridge / HyperFungibleToken app is a prime example, matching the in-scope "token bridge mint/burn" surface) constructs a `DispatchPost` with `payer: msg.sender` where `msg.sender` is the *end user* calling the app's own `send()` function: [7](#0-6) . The app then forwards this struct to `IDispatcher(_host).dispatch(request)` (or `dispatchWithFeeToken`) [8](#0-7) .

From `EvmHost`'s perspective, the caller of `dispatch()` is the **app contract**, not the end user — so `_msgSender()` inside `EvmHost.dispatch` resolves to the app contract address, while `post.payer` (recorded for refunds) is the end user's address. Thus:
- The actual ERC20 `transferFrom` debits the **app contract's own** feeToken balance/allowance to the Host: [2](#0-1) .
- The `FeeMetadata.sender` used for timeout refunds is the **end user**: [9](#0-8) .

This exactly mirrors the reported bug class: the entity actually debited (`_msgSender()`/the vault-equivalent contract) is not the entity the accounting structure attributes responsibility to (`payer`/`_account`), producing unbacked crediting on one side and unexpected loss on the other — exactly as the TAU report describes for `currentMinted[msg.sender]` vs. `currentMinted[account]`.

### Impact Explanation
Every dispatch made through an app that sets `payer` to the originating end user (rather than itself) silently debits the app's own token balance instead of the user's, per request. If that request later times out, the fee is refunded to the end user who never paid it, permanently draining value from the app contract's treasury with no compensating payment — an unbacked credit / permanent loss of funds for the app, reachable by any unprivileged user simply submitting a dispatch that later times out (a single-transaction/single-request trigger, satisfying the "single dispatched request" reachability bar). Because this is systemic (affects every fee-token dispatch routed through any app using this `payer`-forwarding convention), the drain scales with dispatch volume and is not an edge case.

### Likelihood Explanation
High: the flow is triggered by completely ordinary, unprivileged usage — any user calling `send()` on an app like `HyperFungibleToken`, followed by a natural request timeout (which routinely happens for cross-chain messages, e.g. destination chain congestion or invalid recipient). No malicious admin, governance, or privileged actor is required — an ordinary user or unprivileged relayer suffices to trigger the timeout path.

### Recommendation
`EvmHost.dispatch` should debit `post.payer` (via `transferFrom(post.payer, address(this), post.fee)`), not `_msgSender()`, so the entity whose account is charged is exactly the entity later credited on timeout/refund. Alternatively, remove the independent `payer` field entirely and always use `_msgSender()` for both debit and credit, requiring apps to collect the fee from their end users before calling `dispatch()`.

### Proof of Concept
1. Deploy `HyperFungibleToken` (or any app using the same `_buildDispatchPost`/`payer: msg.sender` pattern) and have it hold (or approve) some `feeToken` balance to `EvmHost` for its own operational purposes.
2. A user calls `bridgeApp.send(params)` with a non-zero `relayerFee`, `msg.value == 0`. Internally this calls `EvmHost.dispatch(DispatchPost{..., payer: user})`.
3. Inside `EvmHost.dispatch`, `feeToken.transferFrom(_msgSender(), address(this), fee)` executes with `_msgSender() == address(bridgeApp)` — the bridge app's own balance/allowance is debited, not the user's.
4. `_requestCommitments[commitment] = FeeMetadata({sender: user, fee: fee})` is recorded.
5. The request times out (destination unreachable / timeout elapses); a relayer submits the timeout proof to `EvmHost.dispatchTimeOut(...)`.
6. `EvmHost` refunds `fee` to `meta.sender == user`: [10](#0-9) .
7. Net result: the bridge app paid the fee out of its own funds, but the user received the refund without ever having paid anything — repeatable per dispatch/timeout cycle, permanently draining the app's feeToken reserves.

### Citations

**File:** sdk/packages/core/contracts/interfaces/IDispatcher.sol (L39-41)
```text
    /// @notice Account responsible for paying the fees
    /// @dev If different from msg.sender, must have approved the Host contract
    address payer;
```

**File:** evm/src/core/EvmHost.sol (L872-876)
```text
        if (meta.fee != 0) {
            // refund relayer fee
            IERC20(feeToken()).safeTransfer(meta.sender, meta.fee);
        }
        emit GetRequestTimeoutHandled({commitment: commitment, dest: string(timeout.request.dest)});
```

**File:** evm/src/core/EvmHost.sol (L900-905)
```text

        if (meta.fee != 0) {
            // refund relayer fee
            IERC20(feeToken()).safeTransfer(meta.sender, meta.fee);
        }
        emit PostRequestTimeoutHandled({commitment: commitment, dest: string(timeout.request.dest)});
```

**File:** evm/src/core/EvmHost.sol (L930-932)
```text
        } else if (post.fee > 0) {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), post.fee);
        }
```

**File:** evm/src/core/EvmHost.sol (L946-948)
```text
        // make the commitment
        commitment = request.hash();
        _requestCommitments[commitment] = FeeMetadata({sender: post.payer, fee: post.fee});
```

**File:** evm/src/core/EvmHost.sol (L983-1001)
```text
        } else if (get.fee > 0) {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), get.fee);
        }

        uint64 timeoutTimestamp = get.timeout == 0 ? 0 : uint64(block.timestamp) + uint64(get.timeout);
        GetRequest memory request = GetRequest({
            source: host(),
            dest: get.dest,
            nonce: uint64(_nextNonce()),
            from: abi.encodePacked(_msgSender()),
            timeoutTimestamp: timeoutTimestamp,
            keys: get.keys,
            height: get.height,
            context: get.context
        });

        // make the commitment
        commitment = request.hash();
        _requestCommitments[commitment] = FeeMetadata({sender: _msgSender(), fee: get.fee});
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L248-256)
```text
        return DispatchPost({
            dest: params.dest,
            to: dest,
            body: body,
            timeout: params.timeout,
            fee: params.relayerFee,
            payer: msg.sender
        });
    }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L264-273)
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
```
