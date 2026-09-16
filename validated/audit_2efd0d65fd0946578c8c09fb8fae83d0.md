### Title
Missing sender-module authentication on governance-only `RequestKind`s in `IntentGatewayV2`/`ExtrinsicIntents.onAccept` allows forged `Execute` delegatecall takeover - ([File: evm/src/apps/intentsv2/ExtrinsicIntents.sol])

### Summary
`ExtrinsicIntents.onAccept` authenticates `RedeemEscrow`/`RefundEscrow` requests by checking `request.from` against the registered peer gateway address, but for the privileged kinds `NewDeployment`, `UpdateParams`, `SweepDust`, and `Execute` it only checks that `request.source` equals the Hyperbridge chain id — it never checks `request.from`. Because `pallet-ismp`'s low-level `IsmpDispatcher::dispatch_request` builds the outgoing `PostRequest` from a caller-supplied `DispatchPost` and does not bind `from` to the identity of the dispatching pallet/module, any pallet on the Hyperbridge/Nexus chain that exposes a dispatch path with attacker-influenced `to`/`body` can forge a message that Hyperbridge's own governance is supposed to be the exclusive author of. `RequestKind.Execute` performs `Address.functionDelegateCall(ERC1967Utils.getImplementation(), incoming.request.body[1:])` with the host still as `msg.sender`, so a forged `Execute` body can call the host-only `upgradeToAndCall(address,bytes)`, replacing the gateway's implementation with attacker-controlled bytecode.

### Finding Description
`_authenticate()` in `ExtrinsicIntents.sol` correctly validates `request.from` against the registered peer instance for user-facing withdrawal kinds: [1](#0-0) 

But the governance-only branch of `onAccept` authenticates solely by source chain, never by sender module: [2](#0-1) 

`RequestKind.Execute` delegatecalls the live implementation with attacker-supplied calldata while `msg.sender` (the host) is preserved, satisfying `onlyHost` on sensitive functions such as `upgradeToAndCall`: [3](#0-2) [4](#0-3) 

On the Polkadot side, `pallet-ismp`'s dispatcher builds the `PostRequest` with `source` fixed to the chain's own `HostStateMachine`, but `from`/`to`/`body` come straight from the caller-supplied `DispatchPost` with no binding to the calling pallet's real module id: [5](#0-4) 

This is the documented, standard integration pattern for third-party pallets (`from`, `to`, `body` all caller-controlled in the extrinsic): [6](#0-5) 

The legitimate governance path (`intents-coprocessor` pallet) does gate its own `execute_on_gateway`/`upgrade_gateway` calls behind `T::GovernanceOrigin`: [7](#0-6) 

but the receiving contract has no independent way to tell a genuine governance-authored message apart from any other pallet's message with `source == Hyperbridge`, since it never inspects `request.from`. Any current or future pallet/module on the coprocessor chain that lets a caller pick an arbitrary destination address and body when dispatching (the sanctioned integration pattern shown in the docs) can therefore impersonate Hyperbridge governance to every `IntentGatewayV2` instance across all connected EVM chains.

### Impact Explanation
A successful forgery of `RequestKind.Execute` lets an attacker delegatecall `upgradeToAndCall(maliciousImplementation, initData)` on the gateway, which is host-only but reachable because `msg.sender` is the host contract throughout the delegatecall chain. This grants the attacker full code-execution control over the gateway proxy — equivalent to unauthenticated remote code execution in the CVE-2021-3129 analogy — enabling theft of all escrowed order funds (`_orders` mapping), arbitrary minting/redirection of `_withdraw` flows, and permanent compromise of every deployed `IntentGatewayV2` instance that trusts messages "from Hyperbridge."

### Likelihood Explanation
Exploitation requires an on-chain path on the Hyperbridge/Nexus coprocessor that lets an unprivileged caller pick both the destination module `to` and an attacker-controlled `body` for a dispatched Post request; the low-level `IsmpDispatcher::dispatch_request` in `pallet-ismp` places no restriction on this by design, and the documentation explicitly recommends this exact free-form pattern for pallet authors. I was not able to confirm within the indexed code whether a currently deployed, non-restricted (signed-origin) pallet in the shipped `gargantua`/`nexus` runtimes exposes a fully attacker-controlled `(to, body)` dispatch today (the one example found, `pallet_ismp_demo::dispatch_to_evm`, hardcodes its body and cannot be used to construct an `Execute` payload) — this is a gap in my analysis that would need direct code/config verification of every pallet wired into the runtime's `IsmpDispatcher`.

### Recommendation
Require `IntentsBase`/`ExtrinsicIntents.onAccept` to authenticate governance-only `RequestKind`s (`NewDeployment`, `UpdateParams`, `SweepDust`, `Execute`) by checking `request.from` against a fixed, dedicated governance module id (e.g., `PALLET_INTENTS_ID` as used in `intents-coprocessor::dispatch`), mirroring the `_authenticate()` check already used for `RedeemEscrow`/`RefundEscrow`, rather than relying on `request.source` alone. Additionally, consider hardening `pallet-ismp`'s dispatcher to bind or attest the outgoing `from` field to the actual calling pallet, closing the framework-level spoofing primitive for any future integrator.

### Proof of Concept
1. Identify (or introduce, per the documented pattern) any pallet `X` on the Hyperbridge/Nexus chain wired to `T::IsmpDispatcher = pallet_ismp::Pallet<Runtime>` that lets a signed user pick `to` and `body` for a `DispatchPost` (per `docs/content/developers/polkadot/dispatching.mdx`).
2. From an unprivileged account, call `X`'s dispatch extrinsic with `dest = <EVM chain hosting IntentGatewayV2>`, `to = <IntentGatewayV2 address>`, `body = 0x05 || abi.encodeWithSelector(upgradeToAndCall.selector, attackerImpl, initData)` (`0x05` = `RequestKind.Execute`).
3. `pallet_ismp::dispatch_request` sets `request.source = HostStateMachine::get()` (Hyperbridge/Nexus) regardless of which pallet called it — see `modules/pallets/ismp/src/dispatcher.rs:128-146`.
4. A relayer delivers the message; `HandlerV2`/host calls `IntentGatewayV2.onAccept`, which only checks `keccak256(incoming.request.source) == keccak256(hyperbridge())` (true) and executes `RequestKind.Execute`, delegatecalling `upgradeToAndCall(attackerImpl, initData)` with `msg.sender == host` — satisfying `onlyHost`.
5. The gateway's implementation is now `attackerImpl`; the attacker drains all escrowed funds via arbitrary logic on subsequent calls.

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L63-67)
```text
    function _authenticate(PostRequest calldata request) internal view {
        if (request.from.length != 20) revert InvalidInput();
        address module = address(bytes20(request.from));
        if (_instance(request.source) != module) revert Unauthorized();
    }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L90-98)
```text
    /**
     * @dev Points the proxy at `newImplementation` and delegatecalls `data` on it in the same
     * transaction, e.g. `migrate(relayer)`. Host-only, so reachable only through `Execute`.
     * @param newImplementation The implementation to install; must have code.
     * @param data Migration calldata run against the new implementation, or empty.
     */
    function upgradeToAndCall(address newImplementation, bytes calldata data) external onlyHost {
        ERC1967Utils.upgradeToAndCall(newImplementation, data);
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L112-120)
```text
        /**
         * @dev Delegatecall the current implementation with the rest of the body as calldata, the
         * host still `msg.sender`. Governance's one door to the host-only functions:
         * `upgradeToAndCall` for upgrades, `setRelayer` for rotations. Same discriminator as the
         * `UpgradeContract` action of earlier implementations, whose `(address, bytes)` body
         * selects no function here and reverts.
         */
        Execute
    }
```

**File:** modules/pallets/ismp/src/dispatcher.rs (L128-146)
```rust
			DispatchRequest::Post(dispatch_post) => {
				let post = PostRequest {
					source: self.host_state_machine(),
					dest: dispatch_post.dest,
					nonce: self.next_nonce(),
					from: dispatch_post.from,
					to: dispatch_post.to,
					timeout_timestamp: if dispatch_post.timeout == 0 {
						0
					} else {
						<T::TimestampProvider as UnixTime>::now()
							.as_secs()
							.saturating_add(dispatch_post.timeout)
					},
					body: dispatch_post.body,
				};
				Request::Post(post)
			},
		};
```

**File:** docs/content/developers/polkadot/dispatching.mdx (L57-76)
```text
```rust showLineNumbers
#[pallet::weight(T::dispatch())]
#[pallet::call_index(0)]
pub fn send_message(
    origin: OriginFor<T>,
    post: DispatchPost,
    fee: T::Balance,
) -> DispatchResultWithPostInfo {
    let signer = ensure_signed(origin)?;
    let dispatcher = pallet_ismp::Pallet::<Runtime>::default();
    let commitment = dispatcher.dispatch_request(
        DispatchRequest::Post(post),
        FeeMetadata {
            payer: signer,
            fee,
        }
    )?;

    Ok(())
}
```

**File:** modules/pallets/intents-coprocessor/src/lib.rs (L825-844)
```rust
		#[pallet::call_index(19)]
		#[pallet::weight(T::WeightInfo::upgrade_gateway())]
		pub fn execute_on_gateway(
			origin: OriginFor<T>,
			state_machine: StateMachine,
			data: Vec<u8>,
		) -> DispatchResult {
			T::GovernanceOrigin::ensure_origin(origin)?;

			let gateway_info =
				Gateways::<T>::get(state_machine).ok_or(Error::<T>::GatewayNotFound)?;

			let body = RequestKind::Execute { data }.encode_body();

			Self::dispatch(state_machine, gateway_info.gateway, body)?;

			Self::deposit_event(Event::GatewayCallDispatched { state_machine });

			Ok(())
		}
```
