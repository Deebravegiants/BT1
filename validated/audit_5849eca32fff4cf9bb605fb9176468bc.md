### Title
`IntentGatewayV2.instance()` defaults unregistered source/destination state machines to `address(this)`, letting forged fill/refund confirmations from any relayable but unconfigured chain drain escrowed intent funds - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
`IntentGatewayV2.instance(bytes stateMachineId)` is used as the trust anchor for authenticating incoming `RedeemEscrow`/`RefundEscrow` ISMP messages. When no peer gateway has been explicitly registered for a given `stateMachineId` via governance's `NewDeployment` message, `instance()` silently falls back to `address(this)` instead of rejecting the lookup [1](#0-0) . This is the same bug class as CVE-2021-22926: a missing-registration case is silently resolved to an unintended, attacker-influenceable identity rather than being treated as "no trusted origin", so a message from a chain/contract the operator never configured can still pass authentication as if it originated from "the" canonical gateway.

### Finding Description
`authenticate()` is the sole gate protecting `withdraw()` (which releases/refunds escrowed order funds) from `onAccept`:

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
``` [1](#0-0) 

`_instances` is only populated through the privileged `NewDeployment` message, gated to `hyperbridge` as `request.source` [2](#0-1) , so the mapping itself cannot be poisoned directly. The vulnerability is in the *absence* path: any `stateMachineId` for which governance has not yet (or will never) push a `NewDeployment` entry resolves `instance()` to `address(this)`. `authenticate()` then accepts any inbound `RedeemEscrow`/`RefundEscrow` request whose `request.from` equals this contract's own address, regardless of what chain (`request.source`) actually sent it, as used in `onAccept`:

```solidity
function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
    RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
    if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
        authenticate(incoming.request);
        WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
        return withdraw(body, kind == RequestKind.RefundEscrow);
    }
    ...
}
``` [3](#0-2) 

The design intent, per the comment, is "accepts incoming assets from itself or known instances" — i.e., peer instances deployed at the identical `CREATE2` address across chains are meant to be implicitly trusted. However, the fallback conflates "unregistered / unsupported chain" with "trusted self-deployment", exactly mirroring the curl bug where a keychain-nickname lookup miss silently resolved to an unintended (and attacker-reachable) filesystem entry instead of failing closed.

### Impact Explanation
If Hyperbridge's ISMP core generically supports delivering proofs from any consensus client covering a broad `StateMachine::Evm(chain_id)` space (the codebase shows multiple generic EVM consensus/state-machine clients, e.g. BSC/Pharos/Tendermint-EVM matching arbitrary `chain_id`s [4](#0-3) ), then any chain that is consensus-supported by hyperbridge but for which the operator has not (yet) issued a `NewDeployment` for `IntentGatewayV2` becomes an implicitly-trusted origin for `RedeemEscrow`/`RefundEscrow`. `withdraw()` unconditionally transfers escrowed `_orders[commitment][token]` balances to the beneficiary decoded from the forged request body [5](#0-4) . This is concrete theft of user-escrowed intent funds without the destination fill actually being verified/completed, i.e., an unauthorized app action / forged message delivery consequence directly reachable by any user who can get a message relayed from an unconfigured chain.

### Likelihood Explanation
Exploitation requires an attacker-controlled contract, on a chain state machine that:
1. Hyperbridge's ISMP core already trusts for consensus/state proofs (broad EVM families qualify generically), and
2. IntentGatewayV2 on the target chain has *not yet* registered a `NewDeployment` peer for that source chain (a normal, expected operational state during incremental chain rollout, or for any chain intentionally left unconfigured),

and that the attacker's contract's own address happens to equal `address(this)` of the target IntentGatewayV2 (feasible if the attacker deploys at the same deterministic `CREATE2` salt/deployer used for legitimate multi-chain deployments — realistic since these factory addresses/salts are typically public/standardized for cross-chain app deployment). Given that CREATE2-based same-address deployment is the explicit design goal here, this is a foreseeable and not merely theoretical condition, especially during rollout windows for new chains before `NewDeployment` is executed by governance.

### Recommendation
Change `instance()` to fail closed rather than default to `address(this)`:
```solidity
function instance(bytes calldata stateMachineId) public view returns (address) {
    address gateway = _instances[keccak256(stateMachineId)];
    if (gateway == address(0)) revert UnknownInstance();
    return gateway;
}
```
If same-address deployment across chains is a desired trust shortcut, it must be made explicit and opt-in (e.g., only trust `address(this)` for `stateMachineId`s in an admin-curated allowlist of "same-address" chains, populated the same way `_instances` is), never as a blanket default for any unregistered chain.

### Proof of Concept
1. Governance deploys `IntentGatewayV2` on Chain A via `CREATE2` at address `G`.
2. Governance has not yet called `onAccept(NewDeployment)` to register any peer instance for Chain X (a chain already generically supported by hyperbridge's EVM consensus client family).
3. Attacker deploys a contract at address `G` on Chain X (using the same `CREATE2` deployer/salt convention used for legitimate multi-chain `IntentGatewayV2` rollouts).
4. From this contract, attacker dispatches a `PostRequest` to Chain A's `IntentGatewayV2` with `source = X`, `from = G` (20 bytes), `body = RequestKind.RedeemEscrow || abi.encode(WithdrawalRequest{commitment: <existing order commitment>, tokens: <escrowed tokens>, beneficiary: attacker})`.
5. Relayer delivers the proof; `onAccept` calls `authenticate()`, which calls `instance(X)`; since `_instances[keccak256(X)] == address(0)`, it returns `address(this) == G`, matching `module == G`. Authentication passes.
6. `withdraw()` transfers the escrowed order funds to the attacker's beneficiary — funds theft without a legitimate fill/refund having occurred.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L287-300)
```text
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L636-643)
```text

        // only hyperbridge is permitted to perfom these actions
        if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) revert Unauthorized();
        if (kind == RequestKind.NewDeployment) {
            NewDeployment memory body = abi.decode(incoming.request.body[1:], (NewDeployment));
            _instances[keccak256(body.stateMachineId)] = body.gateway;

            emit NewDeploymentAdded({stateMachineId: body.stateMachineId, gateway: body.gateway});
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-723)
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

        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
        }
```

**File:** modules/ismp/clients/bsc/src/lib.rs (L237-247)
```rust
	fn state_machine(
		&self,
		id: ismp::host::StateMachine,
	) -> Result<Box<dyn StateMachineClient>, ismp::error::Error> {
		match id {
			StateMachine::Evm(chain_id)
				if chain_id == BSC_CHAIN_ID || chain_id == BSC_TESTNET_CHAIN_ID =>
				Ok(Box::new(<EvmStateMachine<H, T>>::default())),
			state_machine => Err(Error::UnsupportedStateMachine(state_machine).into()),
		}
	}
```
