## Title
`IntentGatewayV2.instance()` fallback to `address(this)` lets an unregistered source chain forge peer authentication and drain escrowed funds - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

## Summary
The Tron deployment of `IntentGatewayV2` resolves an unknown peer chain's gateway address to `address(this)` instead of reverting. Since `authenticate()` only compares this resolved address against the attacker-controlled `request.from` field, any state machine that is not yet registered as a peer (`_instances[keccak256(source)] == 0`) can be used to forge a `RedeemEscrow`/`RefundEscrow` message that is accepted as if it came from a legitimate registered peer gateway, redirecting escrowed order funds to an attacker-chosen beneficiary.

## Finding Description
`instance()` in the Tron `IntentGatewayV2` deliberately falls back to `address(this)` when no peer is registered for a given state machine, rather than reverting as the canonical EVM implementation does: [1](#0-0) 

```
function instance(bytes calldata stateMachineId) public view returns (address) {
    address gateway = _instances[keccak256(stateMachineId)];
    return gateway == address(0) ? address(this) : gateway;
}

function authenticate(PostRequest calldata request) internal view {
    if (request.from.length != 20) revert InvalidInput();
    address module = address(bytes20(request.from));
    if (instance(request.source) != module) revert Unauthorized();
}
``` [2](#0-1) 

Compare this with the canonical EVM/SDK version, which reverts with `UnknownInstance` for any state machine that has no registered deployment: [3](#0-2) 

`authenticate()` is the only gate protecting `RedeemEscrow`/`RefundEscrow` delivery in `onAccept`: [4](#0-3) 

```
function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
    RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
    if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
        authenticate(incoming.request);
        WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
        return withdraw(body, kind == RequestKind.RefundEscrow);
    }
```

Because `instance()` returns `address(this)` by default for any `request.source` that has no `_instances` entry, an attacker only needs to deliver a validly-proven ISMP `PostRequest` where:
- `source` = any state machine that Hyperbridge's consensus infrastructure will verify a proof for, but which this specific `IntentGatewayV2` deployment has never registered a `NewDeployment` peer for, and
- `from` = the 20-byte encoding of `address(this)` (the gateway's own, publicly known address),

and `authenticate()` will treat the message as coming from a trusted registered peer, since `instance(source) == address(this) == module`. The forged request's `WithdrawalRequest.beneficiary` and `tokens` are fully attacker-controlled (only bounded by `_orders[commitment][token] != 0`, i.e., the attacker must target an already-escrowed order), letting the attacker redirect that escrow's tokens to themselves via `withdraw()`: [5](#0-4) 

This is the direct structural analog of the Ree6 bug (CVE-2022-39302): a per-tenant/per-peer identity check that is supposed to bind a message to its legitimate origin instead falls back to a permissive default, letting a party outside the trusted set ("another guild"/"an unregistered chain") successfully impersonate a trusted target and redirect protected resources (log messages → escrow funds).

## Impact Explanation
Successful exploitation lets an attacker who can produce a valid consensus proof from any chain not yet onboarded as an `IntentGatewayV2` peer redirect the token escrow of any existing order to an address of their choosing — a direct, unauthorized theft of escrowed user funds via forged message delivery. This satisfies the "concrete theft of funds via forged message delivery" bar. Severity is Medium given the constraint that a controllable/attacker-provable source chain not yet registered as a peer must exist (e.g., during incremental chain onboarding, or against a state machine ID that Hyperbridge trusts for consensus but this gateway instance has not yet added).

## Likelihood Explanation
Likelihood depends on the existence of at least one state machine that Hyperbridge's ISMP host will accept proofs for (consensus client already deployed/trusted) but that has not yet had a `NewDeployment` peer registered for this specific `IntentGatewayV2` instance — a state that is expected during rollout of new chains, or if any chain is deliberately left unregistered. Any unprivileged relayer/message submitter able to source or fabricate such a proof can exploit this without any additional privilege.

## Recommendation
Change `instance()` in the Tron `IntentGatewayV2` to revert (e.g. `UnknownInstance`) when no gateway is registered for the given state machine, mirroring the canonical `IntentsBase._instance()` behavior, so `authenticate()` never accepts a forged peer address by default for unregistered chains.

## Proof of Concept
1. Identify a state machine `X` for which Hyperbridge's ISMP host can verify a valid consensus/state proof, but for which this `IntentGatewayV2` instance has never processed a `NewDeployment` request (i.e., `_instances[keccak256(X)] == address(0)`).
2. Locate an existing order with a non-zero escrow entry (`_orders[commitment][token] != 0`) for some token.
3. Construct a `PostRequest` with `source = X`, `to = address(this)`, `from = abi.encodePacked(address(this))`, and `body = abi.encodePacked(uint8(RequestKind.RedeemEscrow), abi.encode(WithdrawalRequest({commitment: commitment, tokens: <matching tokens>, beneficiary: attackerAddress})))`.
4. Deliver this request through the legitimate ISMP host with a valid proof from chain `X` (satisfying `onlyHost`).
5. In `onAccept`, `authenticate()` computes `instance(X) == address(this)` (fallback) and `module == address(this)` (attacker-chosen `from`), so the equality check passes and `withdraw()` transfers the escrowed tokens to `attackerAddress`.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L284-300)
```text
    /**
     * @dev Fetch the IntentGateway contract instance for a chain.
     */
    function instance(bytes calldata stateMachineId) public view returns (address) {
        address gateway = _instances[keccak256(stateMachineId)];
        return gateway == address(0) ? address(this) : gateway;
    }

    /**
     * @dev Checks that the request originates from a known instance of the IntentGateway.
     */
    function authenticate(PostRequest calldata request) internal view {
        if (request.from.length != 20) revert InvalidInput();
        address module = address(bytes20(request.from));
        // IntentGateway only accepts incoming assets from itself or known instances
        if (instance(request.source) != module) revert Unauthorized();
    }
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-714)
```text
    function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        _filled[body.commitment] = beneficiary;

        // redeem escrowed tokens
        uint256 len = body.tokens.length;
        for (uint256 i; i < len;) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (_orders[body.commitment][token] == 0) revert UnknownOrder();

            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
            unchecked {
                ++i;
            }
        }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L401-405)
```text
    function _instance(bytes calldata stateMachineId) internal view returns (address) {
        address gateway = _instances[keccak256(stateMachineId)];
        if (gateway == address(0)) revert UnknownInstance();
        return gateway;
    }
```
