[1](#0-0)

### Citations

**File:** substrate/frame/message-queue/src/lib.rs (L111-120)
```rust
//! # Scenario: Message processing
//!
//! The pallet runs each block in `on_initialize` or when being manually called through
//! [`frame_support::traits::ServiceQueues::service_queues`].
//!
//! First it tries to "rotate" the `ReadyRing` by one through advancing the `ServiceHead` to the
//! next *ready* queue. It then starts to service this queue by servicing as many pages of it as
//! possible. Servicing a page means to execute as many message of it as possible. Each executed
//! message is marked as *processed* if the [`Config::MessageProcessor`] return Ok. An event
//! [`Event::Processed`] is emitted afterwards. It is possible that the weight limit of the pallet
```
