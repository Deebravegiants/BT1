## Analog Found: Self-Fallback in `instance()` Lets a Crafted `from` Address Authenticate as the Tron `IntentGatewayV2` Itself

### Title
Unregistered-chain fallback to `address(this)` in `instance()` lets a spoofed `PostRequest.from` bypass `authenticate()` and drain escrowed order funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Apache bug is a class of "a config surface intended to be tightly scoped silently falls back to a permissive default, letting an unprivileged actor execute an action under an unintended identity." The same shape exists in the Tron `IntentGatewayV2`: instead of rejecting requests from state machines that have no registered gateway deployment, `instance()` defaults to `address(this)`, which `authenticate()` then treats as a valid peer identity — letting anyone who can get a `PostRequest` with `from == address(thisContract)` accepted as if it came from the contract's own trusted counterpart.

### Finding Description
`instance()` in the Tron contract silently substitutes the local contract's own address whenever no deployment is registered for a given `stateMachineId`: [1](#0-0) 

`authenticate()` is the sole gate for `RedeemEscrow` and `RefundEscrow` in `onAccept`, and it only checks that `request.from` equals `instance(request.source)`: [2](#0-1) 

Because `instance()` returns `address(this)` for any unregistered `source`, `authenticate()` accepts any incoming request whose `from` field equals the local gateway's own address, for *any* source chain that has not had a `NewDeployment` governance message applied to this specific instance. `withdraw()` then transfers escrowed tokens to whatever `beneficiary` the attacker encodes in the request body, with no check that the beneficiary matches the original order's solver or owner: [3](#0-2) 

This is a regression relative to the mainline EVM contract, where the equivalent lookup reverts instead of defaulting to self: [4](#0-3) 

`PostRequest.from` on the source chain is set by the origin-chain ISMP host to the address of the dispatching contract (not directly attacker-choosable), but that dispatching contract's address is fully determined by the attacker's own deployment on the source chain (e.g., via `CREATE2`). An attacker can therefore mine a salt so that their dispatching contract's address on a connected-but-unregistered chain collides with the Tron `IntentGatewayV2`'s own address, then dispatch a `RedeemEscrow`/`RefundEscrow` body naming themselves as `beneficiary` for any known, still-escrowed `commitment`.

### Impact Explanation
Any escrowed order funds sitting in `_orders[commitment][token]` for orders whose destination/source chain has not yet had `NewDeployment` registered on this Tron instance (a normal, expected transient state during rollout, or any chain Hyperbridge's coprocessor connects that this app hasn't explicitly onboarded) can be redirected to an attacker-chosen beneficiary — concrete theft of user/solver escrowed funds, which is one of the explicitly in-scope impacts (forged message delivery / unauthorized app action leading to fund theft).

### Likelihood Explanation
Exploitation requires: (1) a connected state machine for which this Tron gateway has no registered `instance` (plausible during onboarding of new chains, or simply any chain Hyperbridge's underlying consensus clients support that this specific intents deployment hasn't configured), and (2) the ability to deploy a contract at an address equal to the Tron gateway's own address on that chain, which is achievable via `CREATE2` salt-grinding on any EVM-compatible chain. No relayer, governance, or admin compromise is needed — a single crafted, legitimately-proven cross-chain message suffices.

### Recommendation
Change `instance()` to revert (e.g., `UnknownInstance`) when no deployment is registered for `stateMachineId`, matching `evm/src/apps/intentsv2/IntentsBase.sol::_instance`, rather than silently returning `address(this)`. Additionally, consider hardening `withdraw()` to validate that `beneficiary` matches the original order's expected recipient/solver rather than trusting the request body unconditionally.

### Proof of Concept
1. Identify a state machine ID `X` that is a chain connected to Hyperbridge but for which the Tron `IntentGatewayV2` has never received a `NewDeployment` message (so `_instances[keccak256(X)] == address(0)`).
2. On chain `X`, use `CREATE2` to deploy a minimal contract at the exact 20-byte address equal to the Tron `IntentGatewayV2` contract's own address.
3. From that deployed contract, dispatch an ISMP `PostRequest` with `dest` = Tron, `to` = the Tron `IntentGatewayV2` address, `source` = `X` (set automatically to the deploying contract's address as `from`), and `body = [RequestKind.RedeemEscrow, abi.encode(WithdrawalRequest({commitment: <known escrowed commitment>, tokens: <escrowed tokens>, beneficiary: <attacker address>}))]`.
4. Once the request is relayed and proven through the standard ISMP membership-proof path, `onAccept` calls `authenticate()`, which computes `instance(X) == address(this)` (fallback) and compares it to `request.from == address(this)` (attacker's deployed contract address) — the check passes.
5. `withdraw()` executes and transfers the escrowed tokens to the attacker-supplied `beneficiary`. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L286-300)
```text
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
