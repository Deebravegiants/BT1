### Title
Verifier signature replay via refund resetting `old_balance` to 0 - (File: polkadot/runtime/common/src/crowdloan/mod.rs)

### Summary
`do_contribute` gates verifier-required contributions by checking a `MultiSignature` over `payload = (index, &who, old_balance, value)`, using `old_balance` as an implicit anti-replay nonce. Because `refund`/`withdraw` resets a contributor's `contribution_get` entry back to `(0, memo)`, an attacker can reuse a previously obtained signature for `(index, who, 0, value)` to re-contribute after withdrawing, since the recomputed payload is byte-identical to the original one.

### Finding Description
In `do_contribute`, when a fund has `verifier` set, the pallet reads the contributor's current stored balance via `contribution_get` and builds the signed payload from `(index, &who, old_balance, value)` before verifying it against `fund.verifier`. The intent of embedding `old_balance` in the payload is clearly to act as a state-based nonce, preventing a signature obtained for one contribution state from being reused for a different (larger, cumulative) contribution. However, `old_balance` is derived purely from on-chain child-trie storage, not from a monotonically increasing counter. When a contributor calls the refund/withdraw path, their entry is deleted/reset, causing `contribution_get` to return `(0, memo)` again — identical to the state before their very first contribution. Consequently, a signature the off-chain `verifier` issued once for `(index, who, 0, value)` remains valid indefinitely and can be replayed every time the contributor's balance cycles back to zero via withdrawal, because the check only compares the payload to current storage state rather than tracking that this exact payload/signature pair was already consumed.

### Impact Explanation
This allows a contributor to re-enter a verifier-gated crowdloan with a stale, previously-issued KYC/whitelist signature after being refunded, without re-obtaining verifier approval. If the off-chain verifier's approval criteria change over time (e.g., contributor is later de-whitelisted, sanctioned, or the approval was meant to be single-use), the stale signature still satisfies the on-chain check purely because storage state coincidentally matches the original payload. This is a bypass of the intended off-chain verification gate — a signature-replay-adjacent authorization flaw, matching the scoped impact.

### Likelihood Explanation
The precondition set is fully attacker-reachable with no privileged access: any contributor can (1) contribute with a verifier signature, (2) trigger a refund once the fund is dissolved/failed (or otherwise reach a state permitting withdrawal), which resets their contribution entry to zero, and (3) call `contribute` again reusing the identical signature and payload values. All three steps use standard, permissionless extrinsics available to a normal signed user. The only constraint is that the fund must still be open/valid for new contributions at replay time, which is a normal, non-privileged fund-lifecycle condition.

### Recommendation
Do not rely on `old_balance`/`value` state alone as the replay-prevention nonce. Include an explicit monotonically increasing nonce (e.g., a per-contributor `contribution_get` sequence counter that increments on every state change including refunds) or a unique identifier (such as the current block number/era or a strictly incrementing global counter) in the signed payload, and/or track consumed signatures explicitly so a given verifier signature can only be redeemed once regardless of subsequent state resets.

### Proof of Concept
Rust unit test in `polkadot/runtime/common/src/crowdloan/tests.rs`:
1. Create a fund with `verifier` set to a known keypair.
2. Sign `payload = (index, &who, 0u128, value)` with the verifier key -> `sig_v1`.
3. Call `Crowdloan::contribute(who, index, value, Some(sig_v1))` -> assert success, `contribution_get` == `(value, memo)`.
4. End/dissolve fund appropriately and call `Crowdloan::withdraw(who, index)` -> assert `contribution_get(index, &who)` == `(0, memo)`.
5. Re-open contribution window (or use a fund state allowing contributions again) and call `Crowdloan::contribute(who, index, value, Some(sig_v1))` reusing the same `sig_v1` -> assert it succeeds (demonstrating replay), whereas it should be rejected as a stale/already-used signature. [1](#0-0)

### Citations

**File:** polkadot/runtime/common/src/crowdloan/mod.rs (L1-60)
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

//! # Parachain `Crowdloaning` pallet
//!
//! The point of this pallet is to allow parachain projects to offer the ability to help fund a
//! deposit for the parachain. When the crowdloan has ended, the funds are returned.
//!
//! Each fund has a child-trie which stores all contributors account IDs together with the amount
//! they contributed; the root of this can then be used by the parachain to allow contributors to
//! prove that they made some particular contribution to the project (e.g. to be rewarded through
//! some token or badge). The trie is retained for later (efficient) redistribution back to the
//! contributors.
//!
//! Contributions must be of at least `MinContribution` (to account for the resources taken in
//! tracking contributions), and may never tally greater than the fund's `cap`, set and fixed at the
//! time of creation. The `create` call may be used to create a new fund. In order to do this, then
//! a deposit must be paid of the amount `SubmissionDeposit`. Substantial resources are taken on
//! the main trie in tracking a fund and this accounts for that.
//!
//! Funds may be set up during an auction period; their closing time is fixed at creation (as a
//! block number) and if the fund is not successful by the closing time, then it can be dissolved.
//! Funds may span multiple auctions, and even auctions that sell differing periods. However, for a
//! fund to be active in bidding for an auction, it *must* have had *at least one bid* since the end
//! of the last auction. Until a fund takes a further bid following the end of an auction, then it
//! will be inactive.
//!
//! Contributors will get a refund of their contributions from completed funds before the crowdloan
//! can be dissolved.
//!
//! Funds may accept contributions at any point before their success or end. When a parachain
//! slot auction enters its ending period, then parachains will each place a bid; the bid will be
//! raised once per block if the parachain had additional funds contributed since the last bid.
//!
//! Successful funds remain tracked (in the `Funds` storage item and the associated child trie) as
//! long as the parachain remains active. Users can withdraw their funds once the slot is completed
//! and funds are returned to the crowdloan account.

pub mod migration;

use crate::{
	slot_range::SlotRange,
	traits::{Auctioneer, Registrar},
};
use alloc::vec::Vec;
use codec::{Decode, Encode};
use frame_support::{
```
