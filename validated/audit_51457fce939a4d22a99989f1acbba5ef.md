Confirmed: the Tron variant `IntentGatewayV2.sol` `onAccept()` at `evm/tron/contracts/apps/IntentGatewayV2.sol:629-635` handles `RedeemEscrow`/`RefundEscrow` by calling `authenticate(incoming.request)` and immediately `withdraw()`ing escrowed funds — with **no `relayer` authorization check** (`_checkRelayer`) before the withdrawal, unlike the EVM `ExtrinsicIntents.sol` implementation which explicitly gates the same action at `evm/src/apps/intentsv2/ExtrinsicIntents.sol:330-336` with `_checkRelayer(incoming.relayer)` before decoding/withdrawing.

### Title
Tron IntentGatewayV2.onAccept skips relayer authorization on escrow withdrawal - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
On the EVM/Solidity `ExtrinsicIntents.sol` implementation, every inbound `onAccept` message — including the fund-releasing `RedeemEscrow`/`RefundEscrow` actions — is gated by `_checkRelayer(incoming.relayer)` before any decoding or fund movement occurs [1](#0-0) . The Tron port of the same contract, `evm/tron/contracts/apps/IntentGatewayV2.sol`, implements the identical `RequestKind.RedeemEscrow`/`RefundEscrow` path but omits this relayer check entirely, calling `authenticate()` and `withdraw()` directly [2](#0-1) .

### Finding Description
`onAccept` is restricted to `onlyHost`, meaning it can only be invoked by the `EvmHost`/Tron-equivalent host contract after `HandlerV2` (or its Tron analog) has verified a state/consensus proof and called `host.dispatchIncoming(request, relayer)` [3](#0-2) . Critically, the `relayer` parameter passed into `IncomingPostRequest` is **whoever called `handlePostRequests`** — `_msgSender()`, with no trusted-forwarder restriction [4](#0-3) . That means any address holding a valid Merkle proof for a legitimately dispatched message (which anyone can relay, since relaying is permissionless) becomes the "relayer" of record for that delivery.

The documented and tested security model (`sdk/packages/core/docs/ai/flows/how-a-cross-chain-delivery-reaches-the-gateway-and-where-the.md:14-22`) explicitly relies on the destination app re-checking `incoming.relayer` against its own configured `_relayer` before trusting the delivery, since "the address checked in step 3 is only as trustworthy as the contract in step 1." This is exactly the check `ExtrinsicIntents.onAccept` performs via `_checkRelayer(incoming.relayer)` [1](#0-0)  and is enforced with dedicated tests such as `testOnAcceptRejectsUnlistedRelayer` (`evm/tests/foundry/IntentGatewayV2Test.sol:4461`) and `testSetRelayerToZeroReopensTheGate` (`evm/tests/foundry/IntentGatewayV2Test.sol:4447`), which shows that when `_relayer` is unset, delivery from *any* address succeeds.

The Tron `IntentGatewayV2.onAccept` implements the same `RedeemEscrow`/`RefundEscrow` withdrawal logic but never calls this relayer gate [2](#0-1) . `authenticate()` (referenced but not shown in full here) validates that the request's `source`/`from` matches a registered peer IntentGateway instance — an authenticity check on the *message content*, not on *who relayed it*. Because relaying is permissionless and the relayer identity is attacker-controlled data (any address can submit a valid proof for any already-dispatched cross-chain message), omitting the relayer gate on the Tron contract is a divergence from the intended defense-in-depth model that the rest of the codebase relies on.

### Impact Explanation
If the Tron deployment truly lacks this check, it is not by itself sufficient for outright fund theft, since `authenticate()` still requires the message to originate from a genuinely registered peer `IntentGatewayV2` instance and to have passed the underlying ISMP consensus/state proof verification. However, it removes a layer of defense that the codebase's own security documentation and test-suite treat as load-bearing: it means the Tron gateway processes escrow releases based purely on message authenticity, without the secondary check that a specific authorized relayer performed the delivery. This weakens replay/DoS-of-relayer-incentive protections and, more importantly, is inconsistent with `ExtrinsicIntents.sol`'s design, where `_checkRelayer` was added specifically to prevent an arbitrary caller who obtains a valid proof from being the one to trigger fund-moving actions (relevant where relayer selection ties into fee/incentive accounting or where a compromised/forged handler could otherwise inject an arbitrary relayer address, as covered by `testForgedHandlerSwapIsRefused` in `evm/tests/foundry/HostManagerTest.sol:225`).

### Likelihood Explanation
Medium: exploitability depends on whether the Tron `EvmHost`/handler analog and the underlying Tron consensus/proof verification are equally hardened; if so, this specific gap is more of a defense-in-depth regression than a directly exploitable path to unbacked withdrawal on its own. But it deviates from the pattern the rest of the codebase treats as mandatory for exactly this class of "who is allowed to trigger an escrow payout" decision, which is the closest analog in this codebase to the Indodax report's core lesson — a withdrawal system that accepts withdrawals without validating the actor who initiated them.

### Recommendation
Add the same `_checkRelayer(incoming.relayer)` (or equivalent) gate to `evm/tron/contracts/apps/IntentGatewayV2.sol::onAccept` before processing `RedeemEscrow`/`RefundEscrow`, mirroring `ExtrinsicIntents.sol`, and audit all other Tron-specific contract ports for the same omission relative to their EVM counterparts.

### Proof of Concept
Not independently reproducible from the index alone — the `authenticate()` function body and the Tron host/handler's proof-verification code were not available in this pass. A background Devin session with full repo access should: (1) read `authenticate()` in full, (2) confirm whether `_relayer`/`_checkRelayer` exists anywhere else in the Tron contract, and (3) write a Foundry/Tron test analogous to `testOnAcceptRejectsUnlistedRelayer` calling `onAccept` with an arbitrary, non-designated relayer address to confirm whether the withdrawal succeeds without reverting.

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L330-336)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            _authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return _withdraw(body, kind == RequestKind.RefundEscrow, true);
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-635)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }
```

**File:** evm/src/core/EvmHost.sol (L794-818)
```text
    function dispatchIncoming(PostRequest memory request, address relayer) external restrict(_hostParams.handler) {
        address destination = _bytesToAddress(request.to);
        uint256 size;
        assembly {
            size := extcodesize(destination)
        }
        if (size == 0) {
            // instead of reverting the entire batch, early return here.
            return;
        }

        // replay protection
        bytes32 commitment = request.hash();
        _requestReceipts[commitment] = relayer;

        (bool success,) = address(destination)
            .call(abi.encodeWithSelector(IApp.onAccept.selector, IncomingPostRequest(request, relayer)));

        if (!success) {
            // so that it can be retried
            delete _requestReceipts[commitment];
            return;
        }
        emit PostRequestHandled({commitment: commitment, relayer: relayer});
    }
```

**File:** evm/src/core/HandlerV2.sol (L204-209)
```text
        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // duplicate request?
            if (host.requestReceipts(leaf.request.hash()) != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.request, _msgSender());
        }
```
