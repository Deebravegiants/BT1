### Title
`IntentGatewayV2.instance()` wildcard fallback allows forged escrow withdrawals from unregistered source chains - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`instance()` falls back to `address(this)` whenever a source chain has no registered peer gateway, and `authenticate()` uses that fallback as the accepted `from` address for `RedeemEscrow`/`RefundEscrow` requests. This is the same bug class as the reported `rs/cors`/fiber advisory: instead of rejecting an unrecognized/unconfigured origin, the code reflects a "wildcard" trusted value (here, the contract's own address) back as if it were the legitimate registered peer, defeating the authentication check.

### Finding Description
`instance()` is defined to fall back to `address(this)` for any state machine not explicitly registered: [1](#0-0) 

`authenticate()` uses this fallback value directly as the trusted sender address: [2](#0-1) 

`onAccept()` calls `authenticate(incoming.request)` for `RedeemEscrow`/`RefundEscrow` before decoding and executing the withdrawal: [3](#0-2) 

Because `onlyHost` only guarantees that the `PostRequest` was proof-verified as genuinely dispatched from `request.source` (a real, ISMP-connected chain) — it does not guarantee `request.source` is a chain this specific `IntentGatewayV2` instance has registered a peer for via `NewDeployment`. For any `request.source` that is *not yet* registered in `_instances`, `instance(request.source)` silently returns `address(this)` instead of failing closed. An attacker who controls (or can dispatch a message from) any real, non-registered but ISMP-supported source chain can therefore set `request.from = abi.encodePacked(address(thisGateway))` (20 bytes matching the destination gateway's own address) and pass `authenticate()`, because `instance(source) == address(this) == module`.

This is a direct origin-validation error: the correct behavior for an unrecognized/unconfigured `source` should be to reject (deny by default), but the code instead reflects a permissive wildcard match — exactly the CORS analog described in the report (wildcard reflecting an arbitrary, uncontrolled value as trusted instead of enforcing strict allow-listing).

### Impact Explanation
`withdraw()` releases real escrowed tokens tied to `body.commitment`, gated only by `_orders[commitment][token] != 0`: [4](#0-3) 

Since `authenticate()` can be bypassed via the wildcard fallback, an attacker who can get a `PostRequest` delivered from any real but unregistered source chain can forge `RedeemEscrow`/`RefundEscrow` messages against **any existing order commitment on the destination chain**, redirecting the escrowed input tokens (and accrued relayer fees) to an attacker-chosen `beneficiary`. This is a concrete theft-of-funds path reachable by an unprivileged intent solver/attacker — a source-authentication bypass leading to unauthorized release of escrowed user/solver funds.

### Likelihood Explanation
Exploitability requires only that the attacker be able to dispatch (or induce dispatch of) an ISMP `PostRequest` from some chain that is a genuine, ISMP-connected state machine but has not yet been registered as a peer gateway for this specific `IntentGatewayV2` deployment (e.g., a newly supported chain, or one deliberately left unregistered). No privileged role, governance compromise, or consensus forgery is needed — it exploits a logic flaw in the authentication fallback itself, reachable by any party able to route a message through Hyperbridge from an unregistered chain identifier.

### Recommendation
Change `instance()`/`authenticate()` to fail closed for unregistered sources: `authenticate` should revert with `UnknownInstance`/`Unauthorized` when `_instances[keccak256(request.source)] == address(0)`, rather than falling back to `address(this)`. Reserve the "self" fallback, if needed at all, strictly for the chain's own known/registered identifier, never as a default for arbitrary unregistered sources.

### Proof of Concept
1. Deploy/operate `IntentGatewayV2` on chain `D`. On `D`, chain `S` has never been registered via `NewDeployment` (`_instances[keccak256(S)] == address(0)`).
2. A legitimate order with commitment `C` exists on `D` with a non-zero escrowed `_orders[C][token]`.
3. Attacker (controlling any contract on real ISMP-connected chain `S`, or otherwise capable of dispatching a message with `source = S`) dispatches a `PostRequest` to `D`'s gateway with:
   - `source = S` (unregistered)
   - `from = abi.encodePacked(address(gatewayOnD))` (the destination gateway's own 20-byte address)
   - `body = RequestKind.RedeemEscrow || abi.encode(WithdrawalRequest{commitment: C, tokens: [...], beneficiary: attacker})`
4. Once delivered by the host (`onlyHost` calls `onAccept`), `authenticate()` computes `instance(S) == address(this) == module` → passes.
5. `withdraw()` transfers the escrowed tokens for commitment `C` to `attacker`, even though no legitimate fill/cancellation occurred on `S`.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L287-290)
```text
    function instance(bytes calldata stateMachineId) public view returns (address) {
        address gateway = _instances[keccak256(stateMachineId)];
        return gateway == address(0) ? address(this) : gateway;
    }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L292-300)
```text
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
