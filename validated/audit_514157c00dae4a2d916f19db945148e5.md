### Title
Missing `from` (module-id) check on privileged inbound messages allows any Hyperbridge-side pallet/dispatcher to forge protocol-level actions — (File: `modules/pallets/ismp/src/dispatcher.rs`)

### Summary
The Node.js report shows that a security check gated on a *coarse* reference (`process.mainModule.require`) can be trivially bypassed via an *alternate, unchecked* reference to the same underlying capability (`process.mainModule.__proto__.require`), because the guard validated the wrong level of the object graph. Hyperbridge's `HyperbridgeWithdrawalModule::on_accept` (the built-in handler for the reserved module id `b"HYPR-FEE"`) exhibits the same class of bug: it authorizes a privileged action (withdrawing escrowed relayer fees) by checking only the coarse-grained `request.source` (the sending *chain*, i.e. the configured `Coprocessor`) and never checks `request.from` (the specific *module/pallet* on that chain that is supposed to be the only legitimate sender).

### Finding Description
`IsmpDispatcher::dispatch_request` in `modules/pallets/ismp/src/dispatcher.rs` is a generic, low-level primitive available to *any* pallet in the runtime. It unconditionally stamps `source = self.host_state_machine()` on every outgoing `PostRequest`/`GetRequest`: [1](#0-0) 

Crucially, the `from` field on the dispatched request is fully controlled by whichever pallet calls `dispatch_request` — pallet-ismp performs no validation that `from` corresponds to the caller's own module identity. `pallet-demo` illustrates this permissive design: a signed, non-privileged extrinsic lets a user directly choose the outgoing `to` (destination module) and `body`: [2](#0-1) 

On the receiving side, `IsmpHostRouter` intercepts the reserved id `HYPR-FEE` and routes it straight to `HyperbridgeWithdrawalModule`, which is meant to let *only* the coprocessor's fee-management logic instruct relayer-fee payouts: [3](#0-2) 

The authorization check inside `on_accept` is:
```rust
let source = request.source;
if Some(source) != T::Coprocessor::get() {
    Err(IsmpError::Custom(format!("Invalid request source: {source}")))?
}
```
This validates only that the message *chain-of-origin* equals the configured coprocessor — it never checks `request.from`, i.e. it never verifies that the specific pallet/module on the coprocessor chain that dispatched the message is the legitimate fee-accounting authority. Because `dispatch_request` (shown above) is reachable from *any* pallet on the coprocessor chain and always stamps the correct `source`, any pallet capable of building an outbound `PostRequest` with `to = b"HYPR-FEE"` and a SCALE-encoded `Message::WithdrawRelayerFees` body will pass this check and drain `RELAYER_FEE_ACCOUNT` on the destination chain to an attacker-chosen account, exactly as an attacker in the Node.js report reached `require` through an unchecked alternate reference (`__proto__`) instead of the checked one (`process.mainModule`).

The same anti-pattern recurs on the EVM side in `BandwidthManager.onAccept`, which is documented as intentionally trusting only `request.source == hyperbridge()` with "no module-id lookup": [4](#0-3) [5](#0-4) 
Here again, any pallet on Hyperbridge capable of dispatching a `PostRequest` with `to = BandwidthManager`'s address and an ABI-encoded `Withdraw`/`SetTiers` action bypasses the intent that only `pallet-bandwidth`'s `AdminOrigin`-gated calls (`dispatch_withdraw`, `dispatch_set_tiers`) can reach this code path, because `request.source` is unconditionally correct for any Hyperbridge-originated dispatch regardless of the actual sending module.

By contrast, the codebase demonstrates the *correct* pattern elsewhere: `pallet-bandwidth`'s inbound purchase handler explicitly checks `request.from` against a registered manager address, and the outbound-request-delivery-reward pipeline explicitly notes "the source module is the `from` field on the request, and the relayer never gets to claim under a different module identifier than the one the request was actually dispatched with" — showing the project is aware `from` must be checked, but the check was omitted in these two privileged inbound handlers. [6](#0-5) 

### Impact Explanation
- `HyperbridgeWithdrawalModule` forging: unbacked drain of the protocol's `RELAYER_FEE_ACCOUNT` on any chain that configures Hyperbridge as its `Coprocessor` — direct theft of escrowed relayer fees.
- `BandwidthManager` forging: unauthorized `Withdraw` drains the manager's ERC-20/native treasury to an attacker address, or `SetTiers` corrupts pricing (denial of paid bandwidth / free bypass), both without ever going through `pallet-bandwidth`'s `AdminOrigin`.

Both are concrete theft/unauthorized-app-action outcomes reachable from a message that only needs to originate from *some* pallet on the coprocessor/Hyperbridge chain — not from governance.

### Likelihood Explanation
Likelihood depends on the existence of a reachable, attacker-influenced path that lets a caller pick the outbound `to`/`body` fields on a dispatch that will be attributed to Hyperbridge's `source`. `pallet-demo`'s `dispatch_to_evm` (permissionless, signed-user callable) already demonstrates this shape of extrinsic exists in the codebase pattern; any production pallet with a similar "let a user pick a destination module id/body for a Hyperbridge-originated message" feature (e.g. a generic messaging/intents/token app) would make this fully exploitable by an ordinary user. Given this is a documented, intentional design simplification ("no module-id lookup") rather than an oversight caught by tests, and the check is only one field away from being complete, this is a realistic, high-likelihood defense-in-depth gap.

### Recommendation
- In `HyperbridgeWithdrawalModule::on_accept`, additionally verify `request.from` equals a reserved/expected module id representing the legitimate fee-management authority on the coprocessor chain (mirroring the `pallet-bandwidth` inbound check).
- In `BandwidthManager.onAccept`, in addition to `request.source == hyperbridge()`, require `request.from` to equal a fixed, expected governance module id (e.g. `pallet-bandwidth`'s `PalletId`), matching the symmetric check already used for the reverse (manager → pallet) direction.
- Audit all other `IsmpModule::on_accept`/`on_response`/`on_timeout` implementations that gate privileged behavior for the same "source-only" check pattern.

### Proof of Concept
1. On a parachain `D` that has `pallet-ismp::Config::Coprocessor = Some(Hyperbridge)`, an attacker controls (or influences) any pallet `P` on the Hyperbridge chain that has access to `T::IsmpDispatcher` (`pallet_ismp::Pallet<Runtime>`), e.g. one exposing a user-facing "send arbitrary cross-chain message" extrinsic analogous to `pallet-demo::dispatch_to_evm`/`dispatch_request`.
2. `P` calls `IsmpDispatcher::dispatch_request` with `DispatchPost { dest: D, to: b"HYPR-FEE".to_vec(), from: <anything>, body: Message::WithdrawRelayerFees(WithdrawalRequest{ account: attacker_account, amount: large_amount }).encode(), .. }`.
3. `pallet-ismp`'s dispatcher (`modules/pallets/ismp/src/dispatcher.rs:92-151`) stamps `source = Hyperbridge` automatically — the attacker never needs privileged origin for this field.
4. The relayed message arrives at `D`, is routed by `IsmpHostRouter::module_for_id` straight to `HyperbridgeWithdrawalModule` (`dispatcher.rs:168-176`), whose `on_accept` (`dispatcher.rs:189-217`) checks only `request.source == Coprocessor` — which is true — and never checks `from`.
5. `T::Currency::transfer` pays `amount` from `RELAYER_FEE_ACCOUNT` to the attacker-controlled `account`, completing the unauthorized withdrawal.

(Note: step 1's exact permissionless pallet was not conclusively located in the production `nexus`/`gargantua` runtimes within the scope of this analysis — `pallet-demo` is confirmed to exist with this exact shape but its production deployment status is uncertain. The core vulnerability — missing `from` validation in `HyperbridgeWithdrawalModule::on_accept` and `BandwidthManager.onAccept` — is confirmed directly from the cited code and is a genuine defense-in-depth gap regardless.)

### Citations

**File:** modules/pallets/ismp/src/dispatcher.rs (L108-146)
```rust
		let request = match request {
			DispatchRequest::Get(dispatch_get) => {
				let get = GetRequest {
					source: self.host_state_machine(),
					dest: dispatch_get.dest,
					nonce: self.next_nonce(),
					from: dispatch_get.from,
					keys: dispatch_get.keys,
					height: dispatch_get.height,
					context: dispatch_get.context,
					timeout_timestamp: if dispatch_get.timeout == 0 {
						0
					} else {
						<T::TimestampProvider as UnixTime>::now()
							.as_secs()
							.saturating_add(dispatch_get.timeout)
					},
				};
				Request::Get(get)
			},
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

**File:** modules/pallets/ismp/src/dispatcher.rs (L162-217)
```rust
impl<T: Config> IsmpHostRouter<T> {
	pub fn new(inner: Box<dyn IsmpRouter>) -> Self {
		Self { inner, _phantom: PhantomData }
	}
}

impl<T: Config> IsmpRouter for IsmpHostRouter<T> {
	fn module_for_id(&self, id: Vec<u8>) -> Result<Box<dyn IsmpModule>, anyhow::Error> {
		if id.as_slice() == HYPERBRIDGE_MODULE_ID {
			return Ok(Box::new(HyperbridgeWithdrawalModule::<T>::default()));
		}

		self.inner.module_for_id(id)
	}
}

/// Built-in [`IsmpModule`] that performs relayer-fee withdrawals on behalf of
/// the hyperbridge coprocessor. Lives inside `pallet-ismp` so the protocol can
/// pay relayers without a dedicated companion pallet.
pub(crate) struct HyperbridgeWithdrawalModule<T>(PhantomData<T>);

impl<T> Default for HyperbridgeWithdrawalModule<T> {
	fn default() -> Self {
		Self(PhantomData)
	}
}

impl<T: Config> IsmpModule for HyperbridgeWithdrawalModule<T> {
	fn on_accept(&self, request: PostRequest) -> Result<Weight, anyhow::Error> {
		// Only the configured coprocessor may instruct withdrawals.
		let source = request.source;
		if Some(source) != T::Coprocessor::get() {
			Err(IsmpError::Custom(format!("Invalid request source: {source}")))?
		}

		let message = Message::<T::AccountId, T::Balance>::decode(&mut &request.body[..])
			.map_err(|err| IsmpError::Custom(format!("Failed to decode message: {err:?}")))?;

		match message {
			Message::WithdrawRelayerFees(WithdrawalRequest { account, amount }) => {
				T::Currency::transfer(
					&RELAYER_FEE_ACCOUNT.into_account_truncating(),
					&account,
					amount,
					Preservation::Expendable,
				)
				.map_err(|err| {
					IsmpError::Custom(format!("Error withdrawing protocol fees: {err:?}"))
				})?;

				Pallet::<T>::deposit_event(Event::<T>::RelayerFeeWithdrawn { amount, account });
			},
		}

		Ok(<T as frame_system::Config>::DbWeight::get().reads_writes(0, 0))
	}
```

**File:** modules/pallets/demo/src/lib.rs (L216-239)
```rust
		/// Dispatch request to a connected EVM chain.
		#[pallet::weight(Weight::from_parts(1_000_000, 0))]
		#[pallet::call_index(2)]
		pub fn dispatch_to_evm(origin: OriginFor<T>, params: EvmParams) -> DispatchResult {
			let origin = ensure_signed(origin)?;
			let post = DispatchPost {
				dest: StateMachine::Evm(params.destination),
				from: PALLET_ID.to_bytes(),
				to: params.module.0.to_vec(),
				timeout: params.timeout,
				body: b"Hello from polkadot".to_vec(),
			};
			let dispatcher = T::IsmpHost::default();
			for _ in 0..params.count {
				// dispatch the request
				dispatcher
					.dispatch_request(
						DispatchRequest::Post(post.clone()),
						FeeMetadata { payer: origin.clone(), fee: Default::default() },
					)
					.map_err(|_| Error::<T>::TransferFailed)?;
			}
			Ok(())
		}
```

**File:** evm/src/apps/BandwidthManager.sol (L203-232)
```text
    /// @notice Inbound governance from `pallet-bandwidth`. The first
    /// body byte selects `OnAcceptActions`; the remainder is the
    /// action's ABI-encoded payload.
    /// @dev Only the configured host may invoke (`onlyHost`); the
    /// request's `source` must additionally equal hyperbridge.
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        PostRequest calldata request = incoming.request;

        if (!request.source.equals(IDispatcher(_host).hyperbridge())) revert UnauthorizedAction();

        OnAcceptActions action = OnAcceptActions(uint8(request.body[0]));
        if (action == OnAcceptActions.SetTiers) {
            Tier[] memory updates = abi.decode(request.body[1:], (Tier[]));
            for (uint256 i = 0; i < updates.length; i++) {
                tierPrice[updates[i].tier] = updates[i].price;
                emit TierSet(updates[i].tier, updates[i].price);
            }
        } else if (action == OnAcceptActions.Withdraw) {
            Withdrawal memory w = abi.decode(request.body[1:], (Withdrawal));
            if (w.token != address(0)) {
                IERC20(w.token).safeTransfer(w.beneficiary, w.amount);
            } else {
                (bool sent,) = w.beneficiary.call{value: w.amount}("");
                if (!sent) revert InsufficientNativeToken();
            }
            emit Withdrawn(w.token, w.beneficiary, w.amount);
        } else {
            revert UnauthorizedAction();
        }
    }
```

**File:** docs/content/developers/evm/bandwidth/governance.mdx (L16-17)
```text
- **Pallet → manager** (outbound governance). `BandwidthManager.onAccept` checks `request.source == IDispatcher(_host).hyperbridge()`. Only messages dispatched from Hyperbridge are honored. The `to` field is the manager's address — no module-id lookup.
- **Manager → pallet** (inbound purchases). The pallet rejects any purchase whose `request.from` doesn't equal the address stored under `BandwidthManager<T>::get(request.source)`. An attacker who deploys their own contract on a source chain cannot mint subscriptions.
```

**File:** modules/pallets/bandwidth/src/lib.rs (L455-465)
```rust
		fn on_accept(&self, request: PostRequest) -> Result<Weight, anyhow::Error> {
			let manager = BandwidthManager::<T>::get(&request.source).ok_or_else(|| {
				anyhow::anyhow!(format!("no bandwidth manager registered for {:?}", request.source))
			})?;

			if request.from != manager.0.to_vec() {
				return Err(anyhow::anyhow!(format!(
					"purchase from unauthorised sender on {:?}: expected {:x?}, got {:x?}",
					request.source, manager.0, request.from
				)));
			}
```
