Based on my research, I found a genuine security gap: the Tron variant of `IntentGatewayV2.sol` is missing a relayer-allowlist gate that was deliberately added to the canonical EVM implementation as a hardening fix.

### Title
Tron `IntentGatewayV2.onAccept` lacks the relayer-allowlist gate present in the EVM implementation, allowing any relayer/forged-handler delivery to execute governance actions - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The mainline EVM `IntentGatewayV2` (via `ExtrinsicIntents.onAccept` at `evm/src/apps/intentsv2/ExtrinsicIntents.sol:330-350`) calls `_checkRelayer(incoming.relayer)` as the very first statement in `onAccept`, before any request body is decoded, restricting every delivery — escrow redemption, refunds, and every governance action (`NewDeployment`, `UpdateParams`, `SweepDust`, `Execute`) — to a single admin-configured relayer address. This was added as an explicit security fix, documented in `sdk/packages/core/docs/ai/changelog/2026-09-03-relayer-allowlist-on-the-intent-gateway.md`, specifically to close the route where a forged/compromised handler reports an arbitrary relayer address on every message, letting an attacker's forged delivery pass app-level gates.

The Tron deployment's `onAccept` at `evm/tron/contracts/apps/IntentGatewayV2.sol:629-683` has no equivalent `_relayer` state, no `_checkRelayer` call, and no `relayer` field checked anywhere in the contract — confirmed by `grep_search` finding zero relayer-gating logic in that file. It relies only on `onlyHost` and, for governance actions, a `source == hyperbridge` check [1](#0-0) .

### Finding Description
`onAccept` in the Tron gateway decodes `RequestKind` from `incoming.request.body[0]` immediately, with no check on `incoming.relayer` at all: [1](#0-0) 

Compare this to the hardened EVM version, where the relayer check runs before the body is even parsed: [2](#0-1) 

This is analogous to the CVE-2021-43858 bug class: a privileged administrative interface (here, the `onAccept` governance dispatch path for `NewDeployment`/`UpdateParams`/`SweepDust`) is missing an authorization check that the maintainers themselves identified as necessary and added everywhere else in the codebase, leaving one deployment target exposed to the exact attack the fix was meant to close. As documented in `sdk/packages/core/docs/ai/decisions/2026-09-03-hostmanager-deliveries-are-gated-too-and-that-does-not-touch.md`, the threat model is: a `SetHostParam`/handler-swap (via a forged consensus proof or compromised host manager) can install a malicious handler that reports a relayer address of the attacker's choosing on every `onAccept` call. On the hardened contracts, that forged report is worthless because it still has to match `_relayer`. On the Tron gateway, no second gate exists — the `source == hyperbridge` check alone is only as trustworthy as the handler that produced the `PostRequest`, and that handler is exactly what a forged-consensus/handler-swap attack replaces.

### Impact Explanation
If an attacker achieves a forged handler swap on the Tron chain (via the same route the EVM fix defends against), they can deliver arbitrary `NewDeployment`, `UpdateParams`, or `SweepDust` governance requests through `onAccept` with no relayer restriction, since the missing gate was the only additional defense-in-depth layer against exactly this scenario. `SweepDust` directly transfers ERC-20/native token balances to an attacker-chosen `beneficiary` [3](#0-2) , and `NewDeployment`/`UpdateParams` let the attacker redirect the registered gateway instance or protocol fee parameters used to authenticate/settle every subsequent cross-chain order, enabling theft of escrowed funds through the `RedeemEscrow`/`RefundEscrow` path.

### Likelihood Explanation
This requires the same precondition the EVM fix was built for (a forged consensus proof / compromised handler enabling a fabricated `PostRequest.source`), which is already a high-severity, non-trivial precondition; the Tron gateway simply removes one layer of defense-in-depth that exists everywhere else in the codebase for that exact scenario, making Tron uniquely exposed relative to the rest of the fleet once that precondition is met.

### Recommendation
Port the `_relayer` / `_checkRelayer` gate (and `setRelayer`, host-only rotation) from `evm/src/apps/intentsv2/ExtrinsicIntents.sol` and `evm/src/apps/intentsv2/IntentsBase.sol` into `evm/tron/contracts/apps/IntentGatewayV2.sol`, calling `_checkRelayer(incoming.relayer)` as the first statement of `onAccept`, consistent with the fix already applied to `HostManager.sol` and the EVM `IntentGatewayV2`.

### Proof of Concept
1. Attacker obtains (or a bug elsewhere grants) the ability to have the Tron chain's registered ISMP handler report an arbitrary `relayer` address on `onAccept` calls (the scenario the `_checkRelayer` gate is designed to neutralize on the EVM side, per `sdk/packages/core/docs/ai/decisions/2026-09-03-hostmanager-deliveries-are-gated-too-and-that-does-not-touch.md`).
2. Attacker crafts a `PostRequest` with `body[0] = RequestKind.SweepDust` and an attacker-controlled `beneficiary`, sourced to appear as `hyperbridge`.
3. `onAccept` on `evm/tron/contracts/apps/IntentGatewayV2.sol` has no `_checkRelayer` to reject this — unlike `ExtrinsicIntents.onAccept`, which would revert with `Unauthorized` for any relayer other than the configured one.
4. `SweepDust` executes, transferring accumulated dust to the attacker's address; the same absence of a relayer gate also applies to `NewDeployment` and `UpdateParams`.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-644)
```text
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
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L661-681)
```text
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
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L330-350)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            _authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return _withdraw(body, kind == RequestKind.RefundEscrow, true);
        }

        // only hyperbridge is permitted to perform these actions
        if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) revert Unauthorized();
        if (kind == RequestKind.NewDeployment) {
            _addDeployment(abi.decode(incoming.request.body[1:], (Deployment)));
        } else if (kind == RequestKind.UpdateParams) {
            _updateParams(abi.decode(incoming.request.body[1:], (ParamsUpdate)));
        } else if (kind == RequestKind.SweepDust) {
            _sweepDust(abi.decode(incoming.request.body[1:], (SweepDust)));
        } else if (kind == RequestKind.Execute) {
            Address.functionDelegateCall(ERC1967Utils.getImplementation(), incoming.request.body[1:]);
        }
    }
```
