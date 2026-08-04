### Title
Malformed/over-depth XCM message in a concatenated HRMP page silently truncates all trailing valid messages in that page - (File: cumulus/pallets/xcmp-queue/src/lib.rs)

### Summary
`Pallet::take_first_concatenated_xcm`/`take_first_concatenated_xcms` decode a raw HRMP page as a stream of back-to-back SCALE-encoded `VersionedXcm` values with no per-message length prefix. When decoding of one message fails (e.g. because its instruction nesting exceeds `MAX_XCM_DECODE_DEPTH`), the pallet cannot resynchronize to the start of the next message, so it logs via `defensive!` and discards the rest of the page — including any well-formed messages placed after the malformed one. An unprivileged user can construct an XCM program (e.g. nested `SetAppendix`) whose SCALE encoding decodes fine under the *sender's* normal (higher) codec recursion limit but exceeds the *receiver's* stricter `MAX_XCM_DECODE_DEPTH`, causing it to be queued successfully outbound and then fail to decode inbound, wiping out any legitimate messages concatenated behind it in the same page.

### Finding Description
The concatenated XCMP format (`Format::ConcatenatedVersionedXcm`) stores multiple `VersionedXcm` messages back-to-back in a single `Vec<u8>` page with no explicit boundary/length markers between messages — the only way to know where one message ends is to successfully decode it. `handle_xcmp_message`/`handle_xcmp_messages` loop, calling the per-message decode helper repeatedly on the remaining slice until it is empty or a decode error occurs; on error the loop `break`s (after a `defensive!` log), discarding whatever bytes remain in that page unread.

`MAX_XCM_DECODE_DEPTH` is applied only at this inbound decode step to bound stack usage while processing untrusted HRMP data. It is not enforced when a message is originally submitted via an extrinsic (e.g. `pallet_xcm::send`/`reserve_transfer_assets` with a custom program): extrinsic call data is decoded using the codec's normal (much higher) default recursion limit, and `pallet_xcm`'s `send` path does not re-decode/re-validate the constructed `Xcm` program against `MAX_XCM_DECODE_DEPTH` before handing it to the router, which simply `encode()`s the `VersionedXcm` into the outbound queue (`OutboundXcmpMessages`). Because the sender-side depth limit is looser than the receiver-side limit, a user can craft a program (deeply nested `SetAppendix`, or nested XCM fields in instructions like `DepositReserveAsset`) that:
- successfully passes through the sender's extrinsic dispatch and gets enqueued to a channel's outbound page, and
- fails `decode_with_depth_limit` on the receiving chain's `take_first_concatenated_xcm(s)`.

Since the outbound page for a given HRMP channel accumulates messages from multiple senders/transactions within the same block (subject to page-size limits), a legitimate user's message that happens to be appended to the same page after the attacker's malformed one is silently dropped along with it, with no error surfaced to the sender and no on-chain trace beyond a `defensive!` log line (which is typically only visible to node operators, not to affected users).

### Impact Explanation
Concrete scoped impact: legitimate, well-formed XCM instructions (e.g., reserve-transfer completions, callback appendices, asset deposits) that are concatenated after a malformed message in the same HRMP page are permanently lost — not retried, not requeued. This can strand assets or callbacks tied to those dropped messages on the destination chain, and the loss is silent from the perspective of both the sender and the affected downstream users, since HRMP delivery is otherwise considered "confirmed" once relayed.

### Likelihood Explanation
The attacker only needs an unprivileged extrinsic path that lets them submit an arbitrary XCM program to be routed over HRMP (e.g. `pallet_xcm::send`, or a reserve-transfer program with a nested `SetAppendix`/nested XCM field), which is a standard, commonly enabled user-facing call. Getting a victim's message concatenated into the *same page* after the attacker's malformed one requires timing (same block, same destination channel, and being ordered after the attacker's message in the page), which is opportunistic rather than guaranteed on every attempt, but is repeatable and can be maximized by an attacker submitting malformed messages frequently to a busy channel to raise the chance of catching legitimate traffic behind them.

### Recommendation
- Enforce `MAX_XCM_DECODE_DEPTH` (or an equivalent limit) at message construction/send time (in `pallet_xcm::send` and other outbound-routing entry points), so no message can ever be enqueued that would fail the receiver's stricter decode limit.
- Alternatively/additionally, change the concatenated format to be self-describing (length-prefixed) so a single malformed/over-depth message can be skipped without losing subsequent messages in the same page, or split each user-originated message into its own page.

### Proof of Concept
Rust unit test in `cumulus/pallets/xcmp-queue/src/tests.rs`:
1. Encode `N` valid `Xcm` instructions (e.g. `ClearOrigin`) as `VersionedXcm`, concatenate their bytes.
2. Append one crafted `Xcm` containing nested `SetAppendix` instructions whose decode nesting exceeds `MAX_XCM_DECODE_DEPTH` (encode succeeds normally since `Encode` has no depth limit), appended as raw bytes.
3. Append `M` more valid `VersionedXcm`-encoded messages after that.
4. Feed the full byte buffer into `Pallet::take_first_concatenated_xcm`/`take_first_concatenated_xcms` (or `handle_xcmp_message`) as if it were one HRMP page.
5. Assert that the first `N` messages are returned/executed successfully, that a `defensive!`/error path is triggered on the over-depth message, and — critically — assert that the trailing `M` valid messages are **not** present in the decoded output / not executed, proving they were silently dropped. [1](#0-0)

### Citations

**File:** cumulus/pallets/xcmp-queue/src/lib.rs (L1-60)
```rust
// Copyright (C) Parity Technologies (UK) Ltd.
// This file is part of Cumulus.
// SPDX-License-Identifier: Apache-2.0

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// 	http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

//! A pallet which uses the XCMP transport layer to handle both incoming and outgoing XCM message
//! sending and dispatch, queuing, signalling and backpressure. To do so, it implements:
//! * `XcmpMessageHandler`
//! * `XcmpMessageSource`
//!
//! Also provides an implementation of `SendXcm` which can be placed in a router tuple for relaying
//! XCM over XCMP if the destination is `Parent/Parachain`. It requires an implementation of
//! `XcmExecutor` for dispatching incoming XCM messages.
//!
//! To prevent out of memory errors on the `OutboundXcmpMessages` queue, an exponential fee factor
//! (`DeliveryFeeFactor`) is set, much like the one used in DMP.
//! The fee factor increases whenever the total size of messages in a particular channel passes a
//! threshold. This threshold is defined as a percentage of the maximum total size the channel can
//! have. More concretely, the threshold is `max_total_size` / `THRESHOLD_FACTOR`, where:
//! - `max_total_size` is the maximum size, in bytes, of the channel, not number of messages.
//! It is defined in the channel configuration.
//! - `THRESHOLD_FACTOR` just declares which percentage of the max size is the actual threshold.
//! If it's 2, then the threshold is half of the max size, if it's 4, it's a quarter, and so on.

#![cfg_attr(not(feature = "std"), no_std)]

pub mod migration;

#[cfg(test)]
mod mock;

#[cfg(test)]
mod tests;

#[cfg(feature = "runtime-benchmarks")]
mod benchmarking;
#[cfg(feature = "bridging")]
pub mod bridging;
pub mod weights;
pub mod weights_ext;

pub use weights::WeightInfo;
pub use weights_ext::WeightInfoExt;

extern crate alloc;

use alloc::{collections::BTreeSet, vec, vec::Vec};
use bitflags::bitflags;
use bounded_collections::{BoundedBTreeSet, BoundedSlice, BoundedVec};
```
