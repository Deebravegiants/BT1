[1](#0-0) [2](#0-1)

### Citations

**File:** polkadot/runtime/parachains/src/hrmp.rs (L28-28)
```rust
use frame_support::{pallet_prelude::*, traits::ReservableCurrency, DefaultNoBound};
```

**File:** polkadot/runtime/parachains/src/hrmp.rs (L57-70)
```rust
pub trait WeightInfo {
	fn hrmp_init_open_channel() -> Weight;
	fn hrmp_accept_open_channel() -> Weight;
	fn hrmp_close_channel() -> Weight;
	fn force_clean_hrmp(i: u32, e: u32) -> Weight;
	fn force_process_hrmp_open(c: u32) -> Weight;
	fn force_process_hrmp_close(c: u32) -> Weight;
	fn hrmp_cancel_open_request(c: u32) -> Weight;
	fn clean_open_channel_requests(c: u32) -> Weight;
	fn force_open_hrmp_channel(c: u32) -> Weight;
	fn establish_system_channel() -> Weight;
	fn poke_channel_deposits() -> Weight;
	fn establish_channel_with_system() -> Weight;
}
```
