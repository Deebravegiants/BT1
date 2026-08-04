[1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** substrate/frame/utility/src/lib.rs (L31-40)
```rust
//! - Pseudonymal dispatch: A stateless operation, allowing a signed origin to execute a call from
//!   an alternative signed origin. Each account has 2 * 2**16 possible "pseudonyms" (alternative
//!   account IDs) and these can be stacked. This can be useful as a key management tool, where you
//!   need multiple distinct accounts (e.g. as controllers for many staking accounts), but where
//!   it's perfectly fine to have each of them controlled by the same underlying keypair. Derivative
//!   accounts are, for the purposes of proxy filtering considered exactly the same as the origin
//!   and are thus hampered with the origin's filters.
//!
//! Since proxy filters are respected in all dispatches of this pallet, it should never need to be
//! filtered by any proxy.
```

**File:** substrate/frame/utility/src/lib.rs (L270-275)
```rust
			let mut origin = origin;
			let who = ensure_signed(origin.clone())?;
			let pseudonym = derivative_account_id(who, index);
			origin.set_caller_from(frame_system::RawOrigin::Signed(pseudonym));
			let info = call.get_dispatch_info();
			let result = call.dispatch(origin);
```

**File:** substrate/frame/utility/README.md (L14-23)
```markdown
- Pseudonymal dispatch: A stateless operation, allowing a signed origin to execute a call from
  an alternative signed origin. Each account has 2 * 2**16 possible "pseudonyms" (alternative
  account IDs) and these can be stacked. This can be useful as a key management tool, where you
  need multiple distinct accounts (e.g. as controllers for many staking accounts), but where
  it's perfectly fine to have each of them controlled by the same underlying keypair.
  Derivative accounts are, for the purposes of proxy filtering considered exactly the same as
  the origin and are thus hampered with the origin's filters.

Since proxy filters are respected in all dispatches of this module, it should never need to be
filtered by any proxy.
```
