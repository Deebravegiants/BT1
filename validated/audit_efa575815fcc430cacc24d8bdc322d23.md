### Title
IntentGatewayV2 (Tron) authenticates unregistered source chains against its own address, allowing forged escrow redemption/refund — ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron variant of `IntentGatewayV2` restricts `RedeemEscrow`/`RefundEscrow` deliveries to "known instances" of the gateway, but its `instance()` helper falls back to `address(this)` for any state machine that has not yet had an explicit `NewDeployment` registered. Combined with `authenticate()`, this means a `PostRequest` whose `from` field equals the gateway's own address is treated as authentic for *every* unregistered source chain — not just genuinely deployed, governance-vetted instances. This is directly analogous to the Liferay CVE-2024-25149 pattern: a "child" resource (an unregistered chain/instance) inherits the trust/membership of the "parent" (the gateway's own registered set) instead of being properly restricted to it.

### Finding Description
`instance()` returns the contract's own address whenever no explicit deployment mapping exists: [1](#0-0) 

```solidity
function instance(bytes calldata stateMachineId) public view returns (address) {
    address gateway = _instances[keccak256(stateMachineId)];
    return gateway == address(0) ? address(this) : gateway;
}

function authenticate(PostRequest calldata request) internal view {
    if (request.from.length != 20) revert InvalidInput();
    address module = address(bytes20(request.from));
    // IntentGateway only accepts incoming assets from itself or known instances
    if (instance(request.source) != module) revert Unauthorized();
}
```

`authenticate()` is the only gate on `RedeemEscrow`/`RefundEscrow` deliveries in `onAccept`: [2](#0-1) 

For any `request.source` state machine that governance has not yet explicitly registered via `NewDeployment` (`_instances[keccak256(stateMachineId)] == address(0)`), `instance()` silently defaults to `address(this)`. This means the "membership restriction" — that a redeem/refund can only originate from a genuinely deployed, governance-approved sibling gateway — is not enforced for the unregistered case. Any account whose address (as encoded in `request.from`) matches `address(this)` on the same/any chain can pass `authenticate()`.

This is a real risk because the codebase's own newer implementation documents that IntentGateway deployments are pinned to the same address across EVM chains via deterministic CREATE2 (see the sibling contract's comment on "preserving the deterministic CREATE2 deployment addresses"): [3](#0-2) 

The canonical (non-Tron) implementation already recognizes and closes this exact gap: `_instance()` reverts with `UnknownInstance()` instead of falling back to `address(this)` when unregistered: [4](#0-3) [5](#0-4) 

The Tron contract was not updated to match, leaving the fallback-to-self ("membership defaults to trusted parent instead of being properly restricted") pattern live.

### Impact Explanation
An attacker can forge a `RedeemEscrow` or `RefundEscrow` `PostRequest` whose `from` bytes equal the Tron gateway's own address, sourced from any state machine that hasn't yet been registered as a known deployment. Once delivered through the standard ISMP relay/proof pipeline and accepted by `onAccept` → `authenticate()` → `withdraw()`, this releases escrowed tokens/native currency to an attacker-chosen `beneficiary` in `WithdrawalRequest.beneficiary`, i.e., direct theft of user-escrowed funds: [6](#0-5) 

### Likelihood Explanation
Reachable by any unprivileged relayer/dispatcher submitting a message that clears normal ISMP consensus/state verification from a source chain the gateway has not yet explicitly registered. No admin or governance compromise is required — the only requirement is that `request.from` matches `address(this)`, which is realistic given the project's own deterministic CREATE2 deployment pattern across EVM-family chains (Tron's EVM-compatible address space included). This is exactly the bug class the maintainers already patched in the mainline EVM implementation, confirming it is a recognized real vulnerability, just left unfixed in the Tron variant.

### Recommendation
Change `instance()` in `evm/tron/contracts/apps/IntentGatewayV2.sol` to revert (e.g. with an `UnknownInstance`-style error) when no explicit deployment is registered for the given state machine, matching the fix already applied in `evm/src/apps/intentsv2/IntentsBase.sol`'s `_instance()`. Do not fall back to `address(this)`.

### Proof of Concept
1. Governance has registered gateways for chains A and B via `NewDeployment`, but chain C (e.g., a new EVM-compatible chain ISMP already relays messages for) has no entry in `_instances`.
2. On chain C, deploy (or control) a contract/account whose address, when packed into 20 bytes, equals the Tron gateway's own address (`address(this)` on Tron) — achievable via the project's deterministic CREATE2 deployment pattern, or simply by using an address that happens to match.
3. From chain C, dispatch a `PostRequest` with `from = address(this)` bytes, `source = chain C`, body encoding `RequestKind.RedeemEscrow` and a `WithdrawalRequest{commitment, tokens, beneficiary: attacker}` referencing an existing escrowed order commitment.
4. A relayer delivers this proven request to the Tron `IsmpHost`, which calls `IntentGatewayV2.onAccept`.
5. `authenticate()` calls `instance(chain C)`, which returns `address(this)` (no registration exists), matching `request.from` — check passes.
6. `withdraw()` executes, transferring the escrowed tokens to the attacker-controlled `beneficiary`.

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L379-393)
```text
    /**
     * @dev Returns the current block number of the host chain. Order deadlines are
     * denominated in the block heights Hyperbridge tracks for each state machine —
     * for Arbitrum chains that is the L2 block number, but the `block.number` opcode
     * there returns the approximate L1 block number, so the ArbSys precompile is
     * queried instead. The chain id check keeps the bytecode identical across all
     * chains, preserving the deterministic CREATE2 deployment addresses.
     * @return The chain-appropriate current block number.
     */
    function _blockNumber() internal view returns (uint256) {
        if (block.chainid == ARBITRUM_ONE || block.chainid == ARBITRUM_NOVA || block.chainid == ARBITRUM_SEPOLIA) {
            return IArbSys(ARB_SYS).arbBlockNumber();
        }
        return block.number;
    }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L395-405)
```text
    /**
     * @dev Resolves the IntentGateway instance address for a given state machine.
     * Reverts with `UnknownInstance` if no remote deployment has been registered for that chain.
     * @param stateMachineId The raw state machine identifier bytes.
     * @return The gateway address for the given state machine.
     */
    function _instance(bytes calldata stateMachineId) internal view returns (address) {
        address gateway = _instances[keccak256(stateMachineId)];
        if (gateway == address(0)) revert UnknownInstance();
        return gateway;
    }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L56-67)
```text
    /**
     * @dev Authenticates an incoming cross-chain post request by verifying that the
     * sender module matches the registered gateway instance for the source chain.
     * Reverts with InvalidInput if the sender address is malformed, or Unauthorized
     * if the sender is not the expected gateway.
     * @param request The incoming post request to authenticate.
     */
    function _authenticate(PostRequest calldata request) internal view {
        if (request.from.length != 20) revert InvalidInput();
        address module = address(bytes20(request.from));
        if (_instance(request.source) != module) revert Unauthorized();
    }
```
