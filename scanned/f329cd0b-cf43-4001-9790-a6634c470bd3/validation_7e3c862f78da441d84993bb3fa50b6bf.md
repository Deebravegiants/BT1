### Title
Proxy `NonTransfer`-style restrictions on parachains do not cover `PolkadotXcm::execute`, letting a proxy move `real`'s local assets via a crafted XCM program - (File: `polkadot/xcm/pallet-xcm/src/lib.rs`, cross-module with `substrate/frame/proxy/src/lib.rs` and parachain `ProxyType::filter` impls, e.g. `cumulus/parachains/runtimes/assets/asset-hub-westend/src/lib.rs`)

### Summary
On several parachain runtimes (Asset Hub, Coretime, Collectives, staking-async parachain), `ProxyType::NonTransfer` (and similar "deny-list" types) is implemented as `!matches!(c, RuntimeCall::Balances{..} | RuntimeCall::Assets{..} | ...)`, which does **not** list `RuntimeCall::PolkadotXcm(..)` and therefore allows it by default. A `NonTransfer` proxy delegate can call `Proxy::proxy(real, NonTransfer, PolkadotXcm::execute{ message: WithdrawAsset+DepositAsset(to attacker), .. })`; `pallet_xcm::execute` converts the resulting `real`-signed dispatch origin into an XCM `Location` and runs the program, which withdraws `real`'s local assets and deposits them to an attacker-chosen beneficiary, functionally performing the exact transfer the proxy type was meant to forbid.

### Finding Description
`Proxy::proxy` (`substrate/frame/proxy/src/lib.rs`, lines 248-262) checks `def.proxy_type.filter(&call)` against the *outer* `RuntimeCall` shape only — it sees `RuntimeCall::PolkadotXcm(pallet_xcm::Call::execute{ message, max_weight })` as an opaque variant and cannot inspect the semantic effect of the embedded `Xcm` program.

Several parachain `InstanceFilter<RuntimeCall>` implementations use a negation/deny-list pattern for `NonTransfer`, e.g. Asset Hub Westend/Rococo:
```
ProxyType::NonTransfer => !matches!(
    c,
    RuntimeCall::Balances { .. } |
        RuntimeCall::Assets { .. } |
        RuntimeCall::NftFractionalization { .. } |
        RuntimeCall::Nfts { .. } |
        RuntimeCall::Uniques { .. } | ...
),
```
`RuntimeCall::PolkadotXcm(..)` is absent from this deny-list, so `filter()` returns `true` for `execute`. The same pattern (no `PolkadotXcm` exclusion) appears in Coretime-Westend, Collectives-Westend, and the staking-async parachain runtime `ProxyType::NonTransfer` filters. This is in contrast to the relay chains (Polkadot/Kusama/Westend/Rococo), whose `NonTransfer` uses an *allow-list* that explicitly comments "Specifically omitting the entire XCM Pallet" and excludes `PolkadotXcm` from the allowed set.

Once the call passes the proxy filter, `Proxy::do_proxy` dispatches it with `RawOrigin::Signed(real)`. In `pallet_xcm::Pallet::execute` (`polkadot/xcm/pallet-xcm/src/lib.rs`, ~lines 350-377):
```rust
let origin_location = T::ExecuteXcmOrigin::ensure_origin(origin)?;
...
ensure!(T::XcmExecuteFilter::contains(&value), Error::<T>::Filtered);
...
T::XcmExecutor::prepare_and_execute(origin_location, message, ...)
```
`ExecuteXcmOrigin` is `EnsureXcmOrigin<RuntimeOrigin, LocalOriginToLocation>` with `LocalOriginToLocation = SignedToAccountId32<...>`, so a `Signed(real)` origin becomes `Location::from(AccountId32{ id: real })`. On the affected runtimes `type XcmExecuteFilter = Everything;`, so there is no further content-based restriction.

The XCM executor then processes the message with that origin. `WithdrawAsset` in `polkadot/xcm/xcm-executor/src/lib.rs` (~lines 947-969) calls `Config::AssetTransactor::withdraw_asset_with_surplus(asset, origin, ...)`, withdrawing directly from `real`'s on-chain balance (the asset transactor resolves the `AccountId32` location back to `real`'s account). A subsequent `DepositAsset`/`TransferAsset` instruction in the same program can send the withdrawn assets to any attacker-controlled `beneficiary` `Location`. This exactly reproduces a balance transfer, bypassing the intent of `NonTransfer`.

No check in this path — proxy filter, `ExecuteXcmOrigin`, `XcmExecuteFilter`, or the executor's barrier/asset-transactor logic — inspects that the *effect* of the embedded XCM program is equivalent to `Balances::transfer`.

### Impact Explanation
An account holder who grants a `NonTransfer`-typed proxy (intended to allow the delegate to perform non-asset-moving actions on their behalf) is fully exposed to arbitrary local-asset theft: the delegate can withdraw `real`'s native or `pallet-assets` balances and deposit them to any account, on any of the affected parachains (Asset Hub Westend/Rococo, Coretime Westend, Collectives Westend, staking-async parachain runtime). This directly violates the "user-controlled assets must remain fully backed and cannot be stolen" invariant and the "proxy scope restrictions must fully bound all asset-moving capabilities" invariant given in the prompt.

### Likelihood Explanation
This requires only:
1. `real` grants a delegate a `NonTransfer` (or similarly deny-list-based) proxy — a common, low-trust proxy grant intended specifically to *prevent* asset movement.
2. The delegate submits a single `Proxy::proxy` extrinsic wrapping `PolkadotXcm::execute` with a `WithdrawAsset`+`DepositAsset` program.

No governance, no special timing, no race condition, and no privileged origin is needed; the delegate is an ordinary signed account interacting through documented, real extrinsic paths (`Proxy::proxy` → `PolkadotXcm::execute`). This is fully reproducible deterministically.

### Recommendation
Add `RuntimeCall::PolkadotXcm(..)` (or at minimum `pallet_xcm::Call::execute`, `send`, `teleport_assets`, `reserve_transfer_assets`, etc.) to the deny-list of `ProxyType::NonTransfer` (and any other proxy type intended to prohibit asset movement) on Asset Hub, Coretime, Collectives, and the staking-async parachain runtimes, matching the relay-chain pattern that already excludes "the entire XCM Pallet." More robustly, `pallet_xcm::Config::XcmExecuteFilter` should not default to `Everything` for locally-executed messages reachable via proxied/delegated origins, or `pallet-proxy` should special-case `pallet_xcm::execute`/`send` to require an explicit permission rather than falling into a negation-based catch-all.

### Proof of Concept
xcm-emulator/pallet integration test (e.g., in `cumulus/parachains/runtimes/assets/asset-hub-westend/tests/tests.rs` or a pallet_proxy+pallet_xcm mock test):

1. Setup: `real` account funded with native balance `N`. Grant `attacker` a `Proxy::add_proxy(real, ProxyType::NonTransfer, 0)`.
2. Build XCM program:
```rust
let message = Xcm(vec![
    WithdrawAsset((Here, N).into()),
    BuyExecution { fees: (Here, small_fee).into(), weight_limit: Unlimited },
    DepositAsset { assets: Wild(All), beneficiary: attacker_location },
]);
```
3. `attacker` calls `Proxy::proxy(real, Some(ProxyType::NonTransfer), Box::new(RuntimeCall::PolkadotXcm(pallet_xcm::Call::execute{ message: Box::new(VersionedXcm::V4(message)), max_weight })))`.
4. Assertions:
   - Expect the dispatch to **fail** with `Error::CallFiltered` (or equivalent) — this is the desired/patched behavior.
   - On the vulnerable code, assert the call **succeeds**, `Balances::free_balance(real)` decreases by `N`, and `Balances::free_balance(attacker)` increases correspondingly, proving the "scope" violation.
   - Fail the test if funds move under a `NonTransfer` proxy grant.