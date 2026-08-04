### Title
Sender's HRMP channel deposit is never unreserved when the counterpart para is offboarded before `process_hrmp_open_channel_requests` runs - ([File: polkadot/runtime/parachains/src/hrmp.rs])

### Summary
In `Pallet::process_hrmp_open_channel_requests`, a confirmed `HrmpOpenChannelRequest` is only turned into an actual `HrmpChannels` entry if `paras::Pallet::<T>::is_valid_para` returns `true` for both `channel_id.sender` and `channel_id.recipient`. If either para has since been scheduled for offboarding (its `ParaLifecycle` flips to an offboarding state immediately, well before the actual removal at the session boundary), the channel is silently not created, yet the request bookkeeping (`HrmpOpenChannelRequests` removal, `HrmpOpenChannelRequestsList` removal, `decrease_open_channel_request_count`, `decrease_accepted_channel_request_count`) still runs unconditionally. The `sender_deposit` amount recorded on the now-deleted `HrmpOpenChannelRequest` is never unreserved anywhere in this code path.

### Finding Description
`hrmp_init_open_channel` reserves `config.hrmp_sender_deposit` from the sender para's sovereign account and stores it as `sender_deposit` inside a new `HrmpOpenChannelRequest`, then pushes the `HrmpChannelId` into `HrmpOpenChannelRequestsList`. `hrmp_accept_open_channel` marks the request `confirmed = true` (reserving the recipient's deposit as well). Both of these are ordinary, unprivileged parachain-origin extrinsics reachable from a parachain's own runtime (via `ensure_parachain`), so any parachain pair can create such a pending, confirmed request.

At the next session boundary, `Pallet::process_hrmp_open_channel_requests` iterates `HrmpOpenChannelRequestsList` and, for every `confirmed` request, checks `paras::Pallet::<T>::is_valid_para(sender) && is_valid_para(recipient)`. `is_valid_para` returns `false` as soon as a para's lifecycle is set to an offboarding state — which happens immediately when offboarding is scheduled (e.g., via lease expiry or deregistration), not only at the following session boundary when the para is actually purged. This creates a window: a request can be confirmed while both paras are still nominally valid, and then one of them can be scheduled for offboarding before the queue is processed in the same or a subsequent session-change finalize call.

When `is_valid_para` fails for either side, the `if` branch that inserts into `HrmpChannels` is skipped — no channel is created — but the surrounding logic (removal of the `HrmpOpenChannelRequests` entry, removal from `HrmpOpenChannelRequestsList`, and the two counter decrements) executes unconditionally regardless of the `is_valid_para` outcome. Nothing in this branch calls `T::Currency::unreserve` for `request.sender_deposit` (or the recipient's deposit). Once the `HrmpOpenChannelRequest` record is deleted, there is no remaining on-chain reference connecting the reserved balance to a request that could later be cancelled or cleaned up — the reserve becomes orphaned.

### Impact Explanation
The sender parachain's sovereign account permanently loses access to `sender_deposit` funds: they remain reserved (not transferable, not usable for future channel deposits) but are not backed by any channel or any open request that could be cancelled via `hrmp_cancel_open_request`. This is a silent, permanent fund lock affecting the invariant that every HRMP deposit must be either applied to a live channel or returned to its owner.

### Likelihood Explanation
The trigger requires (1) two paras to open and confirm an HRMP channel and (2) one of them to be scheduled for offboarding before the pending-request queue is processed at the next session boundary. Para offboarding can originate from ordinary, non-emergency causes (e.g., lease/slot expiry, or a parachain manager voluntarily deregistering), and its lifecycle flag flips immediately rather than atomically with the HRMP queue processing, so the race window is real and reproducible on demand in a controlled test (by scheduling offboarding of the para between `hrmp_accept_open_channel` and the session-change hook that calls `process_hrmp_open_channel_requests`). No attacker signature/origin/weight checks prevent this since both `hrmp_init_open_channel`/`hrmp_accept_open_channel` and para offboarding are legitimate, unprivileged operations from the respective parachain/manager accounts.

### Recommendation
In the `is_valid_para` failure branch of `process_hrmp_open_channel_requests`, explicitly unreserve `request.sender_deposit` from the sender's sovereign account (and the recipient's `hrmp_recipient_deposit` if already reserved) before removing the `HrmpOpenChannelRequests` entry, mirroring the refund logic used in `hrmp_close_channel`/`hrmp_cancel_open_request`.

### Proof of Concept
Rust unit test (in `polkadot/runtime/parachains/src/hrmp/tests.rs` style):
1. Register/onboard two paras `SENDER` and `RECIPIENT`, fund and reserve deposits via `Hrmp::hrmp_init_open_channel` and `Hrmp::hrmp_accept_open_channel`.
2. Assert `Balances::reserved_balance(sender_sovereign_account) == sender_deposit`.
3. Before running the next session-change hook, mark `RECIPIENT` (or `SENDER`) for offboarding (e.g., via the normal deregistration path so `ParaLifecycles` becomes an offboarding state, making `paras::Pallet::<Test>::is_valid_para(RECIPIENT)` return `false`).
4. Run initializer session-change logic that invokes `Hrmp::process_hrmp_open_channel_requests`.
5. Assert: `HrmpChannels::<Test>::get(&channel_id).is_none()` (no channel created), `HrmpOpenChannelRequests::<Test>::get(&channel_id).is_none()` (request removed), and `Balances::reserved_balance(sender_sovereign_account)` is **still equal to `sender_deposit`** (unchanged), demonstrating the deposit is stuck instead of being unreserved back to `0`. [1](#0-0)

### Citations

**File:** polkadot/runtime/parachains/src/hrmp.rs (L1-40)
```rust
// Copyright (C) Parity Technologies (UK) Ltd.
// This file is part of Polkadot.

// Polkadot is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// Polkadot is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with Polkadot.  If not, see <http://www.gnu.org/licenses/>.

use crate::{
	configuration::{self, HostConfiguration},
	dmp, ensure_parachain, initializer, paras,
};
use alloc::{
	collections::{btree_map::BTreeMap, btree_set::BTreeSet},
	vec,
	vec::Vec,
};
use codec::{Decode, Encode};
use core::{fmt, mem};
use frame_support::{pallet_prelude::*, traits::ReservableCurrency, DefaultNoBound};
use frame_system::pallet_prelude::*;
use polkadot_parachain_primitives::primitives::{HorizontalMessages, IsSystem};
use polkadot_primitives::{
	Balance, Hash, HrmpChannelId, Id as ParaId, InboundHrmpMessage, OutboundHrmpMessage,
	SessionIndex,
};
use scale_info::TypeInfo;
use sp_runtime::{
	traits::{AccountIdConversion, BlakeTwo256, Hash as HashT, UniqueSaturatedInto, Zero},
	ArithmeticError,
};

```
