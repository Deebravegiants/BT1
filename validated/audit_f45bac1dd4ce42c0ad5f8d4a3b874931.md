[1](#0-0)

### Citations

**File:** substrate/frame/message-queue/src/lib.rs (L61-66)
```rust
//! This pallet has two entry points for executing (possibly recursive) logic;
//! [`Pallet::service_queues`] and [`Pallet::execute_overweight`]. Both entry points are guarded by
//! the same mutex to error on reentrancy. The only functions that are explicitly **allowed** to be
//! called by a message processor are: [`Pallet::enqueue_message`] and
//! [`Pallet::enqueue_messages`]. All other functions are forbidden and error with
//! [`Error::RecursiveDisallowed`].
```
