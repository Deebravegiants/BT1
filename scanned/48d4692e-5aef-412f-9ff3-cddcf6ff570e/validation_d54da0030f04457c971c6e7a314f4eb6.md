[1](#0-0)

### Citations

**File:** substrate/frame/message-queue/src/lib.rs (L36-45)
```rust
//! The pallet has means to enqueue, store and process messages. This is implemented by having
//! *queues* which store enqueued messages and can be *served* to process said messages. A queue is
//! identified by its origin in the `BookStateFor`. Each message has an origin which defines into
//! which queue it will be stored. Messages are stored by being appended to the last [`Page`] of a
//! book. Each book keeps track of its pages by indexing `Pages`. The `ReadyRing` contains all
//! queues which hold at least one unprocessed message and are thereby *ready* to be serviced. The
//! `ServiceHead` indicates which *ready* queue is the next to be serviced.
//! The pallet implements [`frame_support::traits::EnqueueMessage`],
//! [`frame_support::traits::ServiceQueues`] and has [`frame_support::traits::ProcessMessage`] and
//! [`OnQueueChanged`] hooks to communicate with the outside world.
```
