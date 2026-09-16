### Title
Requests dispatched with `timeout == 0` can never be timed out, permanently pinning `EvmHost`/`RequestCommitments` storage and any escrowed relayer fee - (File: evm/src/core/EvmHost.sol, evm/src/core/HandlerV2.sol)

### Summary
`EvmHost.dispatch()` lets any caller set `timeout = 0`, which the protocol treats as "never expires." Because the destination's timeout handler can only ever process a request whose timeout has actually elapsed, a `timeout == 0` request can never be timed out, and if it is never delivered (e.g. attached fee is `0`, so no relayer bothers), the corresponding `_requestCommitments` entry (and any escrowed fee) is permanently un-reclaimable. This mirrors the jboss-remoting CWE-400 pattern of a resource being held forever because the party controls whether the "closing" message (here, the timeout) can ever be triggered — except here it is enforced by protocol design rather than by omission, and any unprivileged caller can invoke it for the cost of one transaction.

### Finding Description
When dispatching a POST or GET request, the caller supplies `post.timeout`/`get.timeout` as a relative number of seconds. `EvmHost.dispatch(DispatchPost)` computes: [1](#0-0) 

`timeoutTimestamp` is explicitly set to `0` when `post.timeout == 0`, which the developer docs confirm means "Messages will never expire": [2](#0-1) 

The only way to reclaim the `_requestCommitments[commitment]` entry created at dispatch time (and refund any escrowed fee) for a POST or GET request is `dispatchTimeOut`, invoked from `HandlerV2.handlePostRequestTimeouts` / `handleGetRequestTimeouts`, which requires the request to actually have timed out: [3](#0-2) [4](#0-3) 

`request.timeout()` (in `Message.sol`, referenced by both `HandlerV2` timeout handlers) is derived from `timeoutTimestamp`; the standard implementation used throughout the codebase maps a `timeoutTimestamp` of `0` to the maximum `uint64` value precisely so that "no timeout" also means "can never be judged as timed out" (evidenced by the `type(uint64).max` sentinel usage found across `Message.sol`). With `request.timeout() == type(uint64).max`, the check `if (request.timeout() > state.timestamp) revert MessageNotTimedOut();` can never fail, so `handlePostRequestTimeouts`/`handleGetRequestTimeouts` can never be executed for such a request — `dispatchTimeOut` is permanently unreachable and `_requestCommitments[commitment]` can never be deleted through the timeout path.

There is no other on-chain path that clears `_requestCommitments` for an undelivered POST request: delivery to the destination only ever mutates `_requestReceipts` on the *destination* host, not `_requestCommitments` on the *source* host, and the protocol no longer carries `PostResponse` at all: [5](#0-4) 

Because `dispatch()` is fully permissionless and accepts `fee = 0`, any address can call it repeatedly with `timeout = 0` and `to` pointed at an address/module that will never be voluntarily relayed (no relayer profits from a zero-fee delivery), guaranteeing that each call permanently occupies a storage slot in `_requestCommitments` with no possible cleanup. If a non-zero `fee` is attached instead, that fee (already pulled into the `EvmHost` contract via `safeTransferFrom`/the native-token swap in `dispatch()`) becomes similarly stuck: it can only leave the contract via `dispatchTimeOut`'s refund branch, which — as shown — is unreachable for a `timeout == 0` request.

The pallet-ismp side of the protocol documents the exact same invariant and warns about the associated replay/retry design, but does not appear to reject a `timeout == 0` dispatch either (`DispatchPost.timeout`/`DispatchGet.timeout` accept `0` meaning "never expires" identically on the Substrate side): [6](#0-5) 

### Impact Explanation
This is reachable from a single, unprivileged, permissionless transaction to `EvmHost.dispatch()` (or the equivalent pallet-ismp `dispatch_request`/`send_message` extrinsic) — no governance, relayer, or admin role required. Each call with `timeout = 0` permanently inflates on-chain storage with an entry that can never be evicted, satisfying the CWE-400 "uncontrolled resource consumption" bug class the external report describes, but on persistent state rather than transient threads: the resource consumed (contract/pallet storage) is never released, unlike normal requests whose commitments are eventually cleared by timeout processing. When a non-zero fee is attached, this additionally traps the user's escrowed relayer fee in the `EvmHost` contract forever, since it can only be refunded through the (permanently unreachable) timeout path — a concrete freezing-of-funds outcome.

### Likelihood Explanation
High. `timeout = 0` is a documented, first-class, intentional feature ("no timeout"), not an edge case that needs to be discovered; and `dispatch()` charges no fee floor, so the attack is essentially free to repeat at scale, limited only by ordinary gas costs.

### Recommendation
- Either disallow `timeout == 0` at the dispatch layer (require callers to supply a bounded, non-zero timeout, or enforce a protocol-level maximum lifetime after which a "never expires" request is still eventually reclaimable), or
- Provide an alternate, permissionless cleanup path for stale/undelivered request commitments (e.g., a "prove non-delivery after N blocks" mechanism) so that storage and any escrowed fee cannot be pinned indefinitely regardless of the caller-supplied timeout value.

### Proof of Concept
1. Call `EvmHost.dispatch(DispatchPost{ dest: <any tracked state machine>, to: <arbitrary/never-listening module>, timeout: 0, fee: 0, payer: attacker, body: "" })` from any address. [7](#0-6) 
2. Because `fee == 0`, no relayer economically delivers the request to the destination, so `dispatchIncoming` is never called and `_requestReceipts` is never set on the destination host.
3. Because `timeout == 0` maps to `timeoutTimestamp == 0` → `request.timeout() == type(uint64).max`, any attempt to submit a `PostRequestTimeoutMessage` via `HandlerV2.handlePostRequestTimeouts` reverts with `MessageNotTimedOut()` forever. [8](#0-7) 
4. `_requestCommitments[commitment]` set in step 1 is therefore permanently un-deletable; repeating step 1 in a loop grows `EvmHost` storage without bound at negligible cost, and any non-zero `fee` supplied in step 1 is permanently locked in the contract.

**Note on verification limits:** the exact byte-level implementation of the `timeout()` helper in `Message.sol` (confirming the `timeoutTimestamp == 0 → type(uint64).max` mapping) and the precise on-chain mechanism by which relayers are normally paid their POST-request fee on the EVM source host were not directly retrieved in this pass (only strongly implied by multiple `type(uint64).max` references in `Message.sol` and by the absence of any fee-paying mutation of `_requestCommitments` outside `dispatchTimeOut`). A Devin session with full repository access should confirm `Message.sol`'s `timeout()` implementation and the POST-fee withdrawal function directly before treating the fund-freezing portion of this finding as fully confirmed; the storage-pinning/state-bloat portion is directly supported by the cited `EvmHost.sol`/`HandlerV2.sol` code and documentation.

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

**File:** evm/src/core/EvmHost.sol (L921-948)
```text
    function dispatch(DispatchPost memory post) external payable notFrozen returns (bytes32 commitment) {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                post.fee, path, address(this), block.timestamp
            );
        } else if (post.fee > 0) {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), post.fee);
        }

        // adjust the timeout
        uint64 timeoutTimestamp = post.timeout == 0 ? 0 : uint64(block.timestamp) + uint64(post.timeout);
        PostRequest memory request = PostRequest({
            source: host(),
            dest: post.dest,
            nonce: uint64(_nextNonce()),
            from: abi.encodePacked(_msgSender()),
            to: post.to,
            timeoutTimestamp: timeoutTimestamp,
            body: post.body
        });

        // make the commitment
        commitment = request.hash();
        _requestCommitments[commitment] = FeeMetadata({sender: post.payer, fee: post.fee});
```

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L44-44)
```text
| `timeout` | Time in seconds for message validity eg 3600 for a timeout of 1 hour, or 0 for no timeout. ie Messages will never expire. If the timeout is set to a non-zero value, messages that have exceeded this timeout will be rejected on the destination and require user action (timeout message) to revert changes. |
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

**File:** docs/content/protocol/ismp/responses.mdx (L39-44)
```text
/// A response message holds a batch of GetRequests being responded to.
///
/// The protocol no longer carries `PostResponse`; the only responses processed by
/// `handle` are `GetResponse`s constructed on-chain from the state proof. The
/// relayer's job is to ferry the original `GetRequest`s plus the storage proof; the
/// host produces the `GetResponse` itself.
```

**File:** docs/content/protocol/ismp/dispatcher.mdx (L37-39)
```text
    /// Relative from the current timestamp at which this request expires in seconds.
    pub timeout: u64,
}
```
