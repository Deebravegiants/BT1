Found: the Tron `IntentGatewayV2.instance()` function has a critical divergence from the mainline EVM `_instance()` implementation, which breaks the authentication that `withdraw()` relies on.

### Title
Tron `IntentGatewayV2.instance()` falls back to `address(this)` for unregistered chains, allowing forged escrow withdrawal via self-authentication - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`authenticate()` gates the `RedeemEscrow`/`RefundEscrow` paths of `onAccept()`, which call `withdraw()` and transfer escrowed tokens to an attacker-supplied `beneficiary` for an attacker-supplied `amount`, exactly analogous to the reported `erc20Rescue` pattern where a privileged-looking transfer path lacks a real balance/authorization check tying the transfer to legitimate accounting.

### Finding Description
On mainline EVM, `_instance()` reverts with `UnknownInstance` if no gateway is registered for a state machine: [1](#0-0) 

But the Tron variant instead **falls back to `address(this)`** when no instance is registered: [2](#0-1) 

`authenticate()` uses this same `instance()` lookup to verify `request.from == instance(request.source)`. Because `instance()` returns `address(this)` for any unregistered `state_machine`, an attacker can craft a `PostRequest` with:
- `source` = any state machine ID that has never been registered via `NewDeployment` (which is the default state for most chains until Hyperbridge/governance explicitly registers a peer gateway with `NewDeployment`),
- `from` = `abi.encodePacked(address(this))` (the gateway's own address, trivially knowable/public),

and `authenticate()` will pass, since `instance(unregistered_source) == address(this) == module`.

This forged request is then decoded as a `WithdrawalRequest` and passed to `withdraw()`, which transfers `body.tokens[i].amount` of any token to `body.beneficiary` as long as `_orders[body.commitment][token] != 0`: [3](#0-2) 

The only real check is `_orders[body.commitment][token] == 0` (a zero-check, not a magnitude check), mirroring the audited `erc20Rescue` pattern that checks presence but not sufficiency. Since Solidity 0.8's checked arithmetic on `_orders[body.commitment][token] -= amount` will only revert if `amount` strictly exceeds the escrowed balance for that exact commitment/token pair, an attacker only needs to pick a `commitment` that has *any* non-zero escrow for the targeted token (e.g., a live, unfilled order placed by any user) and request an `amount` up to that outstanding escrow, redirecting it to their own `beneficiary` before the legitimate solver/user can claim it.

Whether the message reaches `onAccept` at all still depends on the `onlyHost` modifier and the `_checkRelayer` gate, but neither of those checks the semantic validity of `source`/`from` — they only gate "who submitted the transaction to the host," not "which counterpart application originated the payload." Once relayed (permissionlessly, by anyone, since Hyperbridge messages are delivered by any relayer once the underlying request is committed/dispatched cross-chain), `authenticate()` is the only content-level check, and it is bypassable exactly as described.

### Impact Explanation
An attacker can drain escrowed order inputs (user or solver funds sitting in `_orders[commitment][token]`) to an address of their choosing, by forging a cross-chain message that appears to originate "from itself." This is a direct theft-of-funds vector on the Tron deployment of `IntentGatewayV2`, structurally identical in severity to a lack-of-balance-check bug enabling unauthorized transfer of held funds.

### Likelihood Explanation
Likelihood is High for any Tron IntentGatewayV2 deployment before all relevant state machine IDs are registered via `NewDeployment`, since:
- The `from` field only needs to encode the gateway's own address (public, known).
- `source` just needs to be any state machine that hasn't yet had an instance registered — the default/starting condition for most chains.
- No signature, no proof of an actual counterpart contract emitting the request is required beyond what `authenticate()`/`onAccept` already checks, and that check is defeated by the fallback default.

### Recommendation
Make `instance()` (or at least the internal check used by `authenticate()`) revert on an unregistered state machine, matching the mainline EVM `_instance()` behavior:
```solidity
function instance(bytes calldata stateMachineId) public view returns (address) {
    address gateway = _instances[keccak256(stateMachineId)];
    if (gateway == address(0)) revert UnknownInstance();
    return gateway;
}
```
And update `authenticate()` accordingly so a message from an unregistered source can never satisfy `instance(request.source) == module`.

### Proof of Concept
1. Deploy `IntentGatewayV2` (Tron) at address `G`. No `NewDeployment` has been submitted for state machine `"CHAIN_X"`.
2. A legitimate user places an order on `G`, escrowing `1000 USDC` under `commitment = C` (`_orders[C][USDC] = 1000e6`).
3. Attacker crafts and gets a relayer to deliver a `PostRequest`:
   - `source = "CHAIN_X"` (unregistered)
   - `from = abi.encodePacked(address(G))`
   - `body = [RedeemEscrow, abi.encode(WithdrawalRequest({commitment: C, tokens: [{token: USDC, amount: 1000e6}], beneficiary: attacker}))]`
4. `onAccept` → `authenticate(request)`: `instance("CHAIN_X")` returns `address(G)` (fallback, since unregistered) which equals `module = address(G)` decoded from `from`. Check passes.
5. `withdraw()` executes: `_orders[C][USDC] != 0` → passes; transfers `1000e6 USDC` to `attacker`; `_orders[C][USDC] -= 1000e6` succeeds (no underflow, exact match).
6. Attacker has stolen the user's escrowed `1000 USDC` that should have gone to the legitimate solver/filler on redemption.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L401-405)
```text
    function _instance(bytes calldata stateMachineId) internal view returns (address) {
        address gateway = _instances[keccak256(stateMachineId)];
        if (gateway == address(0)) revert UnknownInstance();
        return gateway;
    }
```

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
