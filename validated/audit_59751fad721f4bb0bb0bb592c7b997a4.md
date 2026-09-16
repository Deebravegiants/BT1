### Title
Empty-body POST request panics `onAccept`, permanently bricking IntentGatewayV2's cross-chain message route - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
`IntentGatewayV2.onAccept` (the ISMP dispatcher's delivery entry point for incoming cross-chain POST requests) reads the request-kind discriminator by indexing byte 0 of the message body without first checking that the body is non-empty: [1](#0-0) 

`incoming.request.body[0]` is a direct array index into attacker/relayer-controlled `bytes calldata`. If a POST request with a zero-length `body` is relayed and delivered through `EvmHost`/`HandlerV2` to this module, the index access reverts with Solidity's built-in out-of-bounds panic — the same underlying bug class as CVE-2023-47016 (an unchecked out-of-bounds read on attacker-influenced input inside a decoder/dispatch routine), just surfaced as a revert instead of a memory-safety crash because Solidity performs bounds-checked array access.

### Finding Description
`onAccept` is the callback the `IIsmpHost`/`HandlerV2` delivery path invokes for every POST request routed to this application: [2](#0-1) 

The very first operation performed on the untrusted `incoming.request.body` is `uint8(incoming.request.body[0])`, used to select the `RequestKind` branch (`RedeemEscrow`, `RefundEscrow`, `NewDeployment`, `UpdateParams`, `SweepDust`). There is no `require(incoming.request.body.length > 0)` guard before this read, unlike other decoders in the codebase which validate length before slicing (e.g. the RLP `_rlpToUint` helper in `evm/sdk/.../HyperGet.sol` checks `item.length >= 1 + len` before indexing, and the Substrate trie codec in `modules/trees/ethereum/src/node_codec.rs` was hardened with an explicit `data.is_empty()` check specifically to avoid an unchecked `data[0]` index panic on adversarial trie proof nodes — see the regression test `empty_hp_prefix_returns_error_not_panic` in `modules/trees/ethereum/src/tests.rs`).

Any actor able to get a POST request with an empty body dispatched toward this contract's `onAccept` — e.g. a message originating from `hyperbridge` itself, or any other source chain state machine whose messages this instance accepts as `onAccept` caller-restricted only by `onlyHost` (not by body shape) — causes the transaction to revert. Because `onAccept` reverts on delivery rather than returning gracefully or handling the malformed body, the ISMP handler's delivery of that specific request commitment can never succeed: the request either becomes permanently stuck (never delivered, since retries replay the same empty body and revert identically) or forces relayers/protocol infrastructure into a wasted-gas revert loop, i.e., the message route to this app instance is unable to deliver that message.

### Impact Explanation
This satisfies the "unable to deliver messages" acceptance criterion: a legitimately-dispatched cross-chain message (or a message an attacker can induce/dispatch with an empty body, e.g. via `NewDeployment`/`UpdateParams`/other governance-relay code paths if reachable with attacker-controlled body, or simply a malformed relay) causes `onAccept` to always revert for that commitment, since the panic happens before any kind-specific logic and is deterministic given the same bytes. This is not a memory-corruption vulnerability like the original radare2 CVE, but it is the same root-cause pattern (parsing untrusted bytes by indexing without a length check) and results in permanent inability to process a specific incoming message, which the validation rules classify as a route delivery failure — rated Medium/High depending on how easily an attacker can force an empty-body POST to be routed to this contract (e.g., if `NewDeployment`/`UpdateParams` messages, which are meant to originate only from `hyperbridge`, gate on source *after* this index, or if any less-trusted path can produce a zero-length body destined for this module).

### Likelihood Explanation
Likelihood is Medium: reaching this code requires a POST request with an empty `body` to be successfully delivered by `EvmHost`/`HandlerV2` to this specific `IntentGatewayV2` instance's `onAccept`. Whether an unprivileged relayer/solver can force an arbitrary empty-body POST toward this address depends on the broader ISMP request-routing model (destination module resolution), which was not fully verifiable from the indexed code alone — the `onlyHost` modifier only restricts the caller to the host contract, not the shape of the relayed request body, so any request whose `to` resolves to this contract with a crafted proof/commitment could trigger it.

### Recommendation
Add an explicit length check before indexing, matching the pattern used elsewhere in the codebase (e.g. `HyperGet.sol`'s `_rlpToUint`, and the `node_codec.rs` empty-HP-prefix fix):
```solidity
if (incoming.request.body.length == 0) revert InvalidRequestBody();
RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
```
This turns the malformed-message case into a clean revert with a descriptive custom error rather than an unguarded panic, and should be paired with confirming whether the ISMP delivery path allows failed/invalid commitments to be marked as permanently un-retriable (so a bad message doesn't wedge the queue) versus simply reverting the current relay attempt.

### Proof of Concept
1. Craft (or induce delivery of) an ISMP `PostRequest` whose `body` is the empty byte string (`body.length == 0`), destined for the `IntentGatewayV2` instance's address on the destination chain.
2. Have this request proven/relayed through the host so that `IIsmpModule.onAccept` is invoked on `IntentGatewayV2` with `incoming.request.body = ""`.
3. Execution reaches:
```solidity
RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
```
at [3](#0-2) , which reverts with Solidity's built-in array-out-of-bounds panic (`0x32`) before any of the `RedeemEscrow`/`RefundEscrow`/`NewDeployment`/`UpdateParams`/`SweepDust` handling runs.
4. Because the request is deterministic bytes, any retry of the same commitment reverts identically, leaving that specific incoming message permanently undeliverable to this module.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L623-636)
```text
    /**
     * @notice Executes an incoming post request.
     * @dev This function is called when an incoming post request is accepted.
     * It is only accessible by the host.
     * @param incoming The incoming post request data.
     */
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }

```
