### Title
Governance-only `Execute` request path in `ExtrinsicIntents.onAccept` validates only the source chain, not the sender module, before delegatecalling the implementation - (File: `evm/src/apps/intentsv2/ExtrinsicIntents.sol`)

### Summary
The `onAccept` handler's Diamond-analog `Execute` branch (and the sibling `NewDeployment`/`UpdateParams`/`SweepDust` branches) authorizes governance-only actions solely by comparing `incoming.request.source` against `IDispatcher(host()).hyperbridge()` — the source *chain* identifier — without verifying `incoming.request.from`, the specific module/pallet address that dispatched the message on that chain.

### Finding Description
`onAccept` in `ExtrinsicIntents.sol` dispatches on the first body byte (`RequestKind`). For `RedeemEscrow`/`RefundEscrow`, the sender is properly authenticated with `_authenticate`, which checks `request.from` against the registered peer gateway instance: [1](#0-0) 

However, for the privileged branches — including `Execute`, which performs `Address.functionDelegateCall(ERC1967Utils.getImplementation(), incoming.request.body[1:])` with the host still as `msg.sender`, reaching host-only functions like `upgradeToAndCall` and `setRelayer` — the only guard is: [2](#0-1) 

This check compares `incoming.request.source` (the chain the message came from) against `hyperbridge()`, but never checks `incoming.request.from` (the specific pallet/account on that chain that dispatched the message). The `Execute` action's own comment acknowledges the intended access model rests entirely on this authorization: [3](#0-2)  and the governance-side implementation confirms it is meant to be reachable only via the coprocessor pallet's `execute_on_gateway` extrinsic, gated by `GovernanceOrigin`: [4](#0-3) .

If any other pallet, contract, or actor on the Hyperbridge chain (the `source` state machine) can dispatch an ISMP post request to this gateway's registered peer address with an `Execute`-tagged body, `onAccept` will accept it as long as `request.source` resolves to the Hyperbridge chain — regardless of which module actually sent it. Since this repo's own delegatecall governance design ("Execute delegatecalls the implementation") explicitly treats `onlyHost` as "the whole access model" once `msg.sender` is preserved as host, the missing `from`-address check on the ISMP message itself is the analog of the Diamond fallback's missing facet whitelist: it lets an unintended sender reach the delegatecall with attacker/other-pallet-controlled calldata, executing `upgradeToAndCall(newImplementation, data)` to swap the proxy's implementation to a malicious contract, or `setRelayer` to redirect all future relayer-gated deliveries.

### Impact Explanation
A successful forged `Execute` delivery can call `upgradeToAndCall` on the intents gateway proxy, installing an attacker-controlled implementation with full delegatecall access to the proxy's storage — including the escrow accounting (`_orders`, `_filled` mappings) — enabling theft of all escrowed order funds and permanent compromise of the gateway. This satisfies the "unbacked mint / theft of funds / unauthorized app action" impact bar.

### Likelihood Explanation
Exploitability depends entirely on whether some other party on the Hyperbridge parachain, besides the intents-coprocessor pallet under `GovernanceOrigin`, can dispatch an ISMP post request whose `from` field equals the registered peer address recognized by `_instance(order.source)`/deployment registration for the Hyperbridge chain. I was not able to fully verify from the index whether `pallet-ismp`'s dispatch enforces `from` to a fixed module id that only the coprocessor pallet can use, or whether the check the audited pattern relies on (`request.source == hyperbridge()`) is in practice sufficient because only one pallet ever dispatches to app instances from that chain. This is the key uncertainty: if `pallet-ismp` restricts `from` per-pallet and no other authorized dispatcher exists on that chain, this reduces to a defense-in-depth gap rather than an exploitable path.

### Recommendation
Add an explicit `from`-address (module) check for all governance-only `RequestKind`s (`NewDeployment`, `UpdateParams`, `SweepDust`, `Execute`), analogous to `_authenticate`, verifying `incoming.request.from` equals a fixed, configured governance module identifier for the Hyperbridge chain — not merely that `incoming.request.source` resolves to that chain.

### Proof of Concept
Not constructable with certainty from the indexed code alone: exploitation requires confirming whether `pallet-ismp`/the Hyperbridge relay chain permits any pallet other than `intents-coprocessor` to dispatch an ISMP post request with `from` spoofable as the gateway's registered governance sender. This would need direct inspection of `modules/pallets/ismp` dispatch/`from` assignment logic, which was not fully retrievable within the available tool budget.

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L63-67)
```text
    function _authenticate(PostRequest calldata request) internal view {
        if (request.from.length != 20) revert InvalidInput();
        address module = address(bytes20(request.from));
        if (_instance(request.source) != module) revert Unauthorized();
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L112-119)
```text
        /**
         * @dev Delegatecall the current implementation with the rest of the body as calldata, the
         * host still `msg.sender`. Governance's one door to the host-only functions:
         * `upgradeToAndCall` for upgrades, `setRelayer` for rotations. Same discriminator as the
         * `UpgradeContract` action of earlier implementations, whose `(address, bytes)` body
         * selects no function here and reverts.
         */
        Execute
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
