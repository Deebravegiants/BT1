## Title
Tron IntentGatewayV2 missing relayer allowlist gate lets any relayer forge escrow settlement and governance delivery — (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The main EVM `IntentGatewayV2` (`evm/src/apps/intentsv2/ExtrinsicIntents.sol`) enforces a relayer allowlist check (`_checkRelayer`) at the top of `onAccept`/`onGetResponse`, before any request body is decoded, so a forged/compromised consensus proof carried by an arbitrary relayer cannot move escrow. The Tron port of the same contract, `evm/tron/contracts/apps/IntentGatewayV2.sol`, implements `onAccept` with only the `onlyHost` modifier and never calls an equivalent relayer check — the relayer allowlist mechanism (`_relayer`, `_checkRelayer`, `setRelayer`) does not exist in this file at all.

### Finding Description
On the reference EVM implementation, `ExtrinsicIntents.onAccept` runs `onlyHost` and then `_checkRelayer(incoming.relayer)` before decoding the `RequestKind`, closing the gap where an untrusted relayer that merely relayed a valid ISMP proof (from `HandlerV2.handlePostRequests`/`handleGetResponses` → `EvmHost.dispatchIncoming`) could be the vector for unauthorized settlement: [1](#0-0) [2](#0-1) 

The Tron port's `onAccept` is otherwise structurally identical (same `RequestKind` dispatch for `RedeemEscrow`, `RefundEscrow`, `NewDeployment`, `UpdateParams`, `SweepDust`), but has no relayer check at all — only `onlyHost` gates entry, and the `IncomingPostRequest.relayer` field is never consulted: [3](#0-2) 

`IncomingPostRequest.relayer` is populated by `EvmHost.dispatchIncoming`/`dispatchIncoming(GetResponse)` with whatever relayer address submitted the ISMP message proof (i.e. `_msgSender()` of the handler call at delivery time), not a value the ISMP protocol itself authenticates as trustworthy for application-level authorization: [4](#0-3) 

The project's own documentation on the relayer gate explicitly frames it as defense against exactly this scenario: an attacker who can get an arbitrary relayer to deliver a message (e.g. through a forged/compromised consensus update) should still be blocked because only the allowlisted relayer's delivery is honored: [5](#0-4) 

Because the Tron gateway lacks this gate entirely, its `RedeemEscrow`/`RefundEscrow` settlement path and its governance actions (`NewDeployment`, `UpdateParams`, `SweepDust`) are reachable by any relayer who can get a message delivered through `onlyHost` (i.e. anyone who can produce a validly-proven ISMP message to this contract's host), with no secondary check on who actually submitted it. This exactly mirrors the reported bug class: a code path that is documented/intended to be restricted (here: restricted to a single trusted relayer, mirroring the wallet-rpc's restricted-mode contract) but the restriction is implemented ad hoc per-contract/per-chain-port and was simply omitted on one variant.

### Impact Explanation
If Tron's ISMP consensus verification for the source chain is ever compromised, downgraded, or misconfigured (the same threat model the relayer allowlist was built to mitigate for the EVM gateway), an attacker able to relay any validly-provable message to this Tron gateway can:
- Trigger `RedeemEscrow`/`RefundEscrow` withdrawals to attacker-controlled beneficiaries once `authenticate()` on the encoded `WithdrawalRequest.beneficiary`/gateway instance is satisfied by a message the attacker otherwise controls the framing of, without the gateway’s designed relayer whitelist acting as a second line of defense.
- Deliver governance-class actions (`NewDeployment`, `UpdateParams`, `SweepDust`) that only check `request.source == hyperbridge()`, without any relayer-level restriction, weakening the gateway's defense-in-depth by one full layer relative to its EVM sibling.

This is a real reduction of the security guarantee the rest of the codebase explicitly relies on ("Once a relayer is set, rejects deliveries from anyone else before the body is read"), representing unauthorized app action / potential theft of escrowed funds on the Tron deployment specifically. Severity is High: it is a missing authorization layer on a fund-moving contract, consistent with the analog report's classification of "Improper Authentication."

### Likelihood Explanation
Likelihood depends on whether Tron's `IntentGatewayV2` is actually deployed to mainnet and whether an attacker can get any relayer to deliver a forged/manipulated proof (the same precondition the analog report itself calls out for the wallet-rpc bug via authenticated-but-still-vulnerable requests). Given that Polytope Labs' own decision log treats "a forged consensus [proof used by] an arbitrary relayer" as a credible enough threat to justify adding this exact gate to every other gateway variant (`HostManager`, `BandwidthManager`, `IntentGatewayV2` EVM/main), the omission in the Tron port is a genuine gap rather than a theoretical one — it was clearly not an intentional design choice for Tron, since it directly parallels code that was hardened everywhere else.

### Recommendation
Port the relayer allowlist mechanism (`_relayer` storage slot, `_checkRelayer`, `setRelayer` host-only setter, `relayer()` getter) from `evm/src/apps/intentsv2/ExtrinsicIntents.sol` into `evm/tron/contracts/apps/IntentGatewayV2.sol`, and call `_checkRelayer(incoming.relayer)` immediately after `onlyHost` at the top of `onAccept` (and the analogous `onGetResponse`, if present), before any request body decoding — mirroring the EVM implementation exactly so the two deployments share the same defense-in-depth posture. Add regression tests analogous to `IntentGatewayV2Test.sol`'s `testOnAcceptRejectsUnlistedRelayer` / `testOnAcceptGovernanceRejectsUnlistedRelayer` for the Tron contract.

### Proof of Concept
Concrete exploitation requires demonstrating that Tron's consensus client can be made to accept a forged/malicious proof (out of scope for this repo-only review — Tron's specific consensus client was not in the retrieved context). The root-cause code proof is the side-by-side comparison of the two `onAccept` implementations:

- EVM (gated): `onlyHost` → `_checkRelayer(incoming.relayer)` → decode body: [1](#0-0) 
- Tron (ungated): `onlyHost` → decode body directly, no relayer check present anywhere in the file: [3](#0-2) 

A grep for `relayer`/`_checkRelayer`/`onlyHost` across the Tron file returns only the 7 `onlyHost`-modifier occurrences and zero relayer-allowlist references, confirming the mechanism's absence, in contrast to its presence and heavy test coverage on the EVM gateway (`ExtrinsicIntents.sol` lines 69–113, and `IntentGatewayV2Test.sol` tests such as `testOnAcceptRejectsUnlistedRelayer`, `testSetRelayerRotates`, `testFreshProxyIsOpenUntilGovernanceArmsIt`).

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L69-78)
```text
    /**
     * @dev Once a relayer is set, rejects deliveries from anyone else before the body is read. The
     * host records the revert as undelivered, so the authorised relayer can resubmit. While unset,
     * every delivery passes: a proxy from before the gate stays open until `migrate` arms it.
     * @param relayer The account that submitted the message to the handler.
     */
    function _checkRelayer(address relayer) internal view {
        address authorised = _relayer;
        if (authorised != address(0) && relayer != authorised) revert Unauthorized();
    }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L330-337)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            _authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return _withdraw(body, kind == RequestKind.RefundEscrow, true);
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L623-683)
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

        // only hyperbridge is permitted to perfom these actions
        if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) revert Unauthorized();
        if (kind == RequestKind.NewDeployment) {
            NewDeployment memory body = abi.decode(incoming.request.body[1:], (NewDeployment));
            _instances[keccak256(body.stateMachineId)] = body.gateway;

            emit NewDeploymentAdded({stateMachineId: body.stateMachineId, gateway: body.gateway});
        } else if (kind == RequestKind.UpdateParams) {
            // Decode the body which includes optional destination-specific protocol fee updates
            ParamsUpdate memory update = abi.decode(incoming.request.body[1:], (ParamsUpdate));
            emit ParamsUpdated({previous: _params, current: update.params});
            _params = update.params;

            // Update destination-specific protocol fees if provided
            for (uint256 i; i < update.destinationFees.length;) {
                bytes32 stateMachineId = update.destinationFees[i].stateMachineId;
                uint256 feeBps = update.destinationFees[i].destinationFeeBps;
                _destinationProtocolFees[stateMachineId] = feeBps;

                unchecked {
                    ++i;
                }
                emit DestinationProtocolFeeUpdated(stateMachineId, feeBps);
            }
        } else if (kind == RequestKind.SweepDust) {
            SweepDust memory req = abi.decode(incoming.request.body[1:], (SweepDust));

            uint256 outputsLen = req.outputs.length;
            for (uint256 i; i < outputsLen;) {
                TokenInfo memory info = req.outputs[i];
                address token = address(uint160(uint256(info.token)));
                uint256 amount = info.amount;

                if (token == address(0)) {
                    (bool sent,) = req.beneficiary.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
                unchecked {
                    ++i;
                }
                emit DustSwept(token, amount, req.beneficiary);
            }
        }
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

**File:** sdk/packages/core/docs/ai/flows/how-a-cross-chain-delivery-reaches-the-gateway-and-where-the.md (L1-22)
```markdown
# How a cross-chain delivery reaches the gateway, and where the relayer gate sits

Verified against `evm/src/core/HandlerV2.sol`, `evm/src/core/EvmHost.sol` and
`evm/src/apps/intentsv2/ExtrinsicIntents.sol`, and exercised by
`testRejectedDeliveryStaysRetryableThroughHost` in `evm/tests/foundry/IntentGatewayV2Test.sol`.

1. A relayer calls `HandlerV2.handlePostRequests` (or `handleGetResponses`). After proof
   verification the handler calls `host.dispatchIncoming(request, _msgSender())`. `_msgSender()` is
   plain `msg.sender`; the handler has no trusted forwarder.
2. `EvmHost.dispatchIncoming` (restricted to the handler) writes a receipt for the request
   commitment, then low-level calls the module with `IApp.onAccept(IncomingPostRequest(request,
   relayer))`. If that call fails the host deletes the receipt and returns without reverting, so the
   rest of the batch proceeds and the message stays deliverable.
3. `ExtrinsicIntents.onAccept` runs `onlyHost`, then `_checkRelayer(incoming.relayer)`, which reverts
   with `Unauthorized` when a relayer is set and the delivery is from anyone else. Only then is the
   first body byte read as a `RequestKind`. `onGetResponse` has the same two steps before touching
   the response.

So a delivery from anyone but the authorised relayer never decodes the body, never runs
`_authenticate`, and leaves no receipt. The authorised relayer submitting the same message later
takes the normal path. A gateway whose `_relayer` is zero accepts every relayer: that is the state
a fresh proxy is in until governance arms it, below.
```
