### Title
Unrecoverable outbound channel suspension via unilateral `ChannelSignal::Suspend` from a sibling parachain - (File: cumulus/pallets/xcmp-queue/src/lib.rs)

### Summary
`XcmpQueue::handle_xcmp_messages` decodes and acts on `ChannelSignal::Suspend`/`ChannelSignal::Resume` frames received from any already-connected sibling parachain without any authorization check beyond channel existence, mutating `OutboundXcmpStatus` for that sender to `OutboundState::Suspended`. Because resumption depends entirely on the same untrusted sender voluntarily sending a subsequent `ChannelSignal::Resume`, a misbehaving/hostile sibling can suspend the local chain's outbound channel to itself indefinitely, with no protocol-level timeout or permissionless recovery path.

### Finding Description
`handle_xcmp_messages` in `cumulus/pallets/xcmp-queue/src/lib.rs` inspects each inbound XCMP page; when the page format is `XcmpMessageFormat::Signals`, it decodes `ChannelSignal` values and dispatches to `suspend_channel(sender)` / `resume_channel(sender)`, which flip the `state` field of the matching entry in `OutboundXcmpStatus` between `OutboundState::Ok` and `OutboundState::Suspended`. [1](#0-0) 

No `ControllerOrigin`, signature, or reputation check gates this transition — any sibling with an already-open HRMP channel controls the raw bytes it sends over that channel and can freely construct a page encoding `(XcmpMessageFormat::Signals, ChannelSignal::Suspend)`. This is consistent with the XCMP transport model, where trust is established once at HRMP-channel-open time (a relay-chain/governance action) but not re-validated per message; individual signal frames are not further authenticated by the pallet.

Once `OutboundXcmpStatus` for that recipient is `Suspended`, the pallet's outbound message service (`XcmpMessageSource::take_outbound_messages`, used by the collator to build XCMP pages) skips assembling/sending further messages to that recipient, including ordinary user-initiated `send_xcm` traffic (asset transfers, XCM programs, etc.) that gets queued behind the suspended channel. The only path back to `OutboundState::Ok` is a subsequent `ChannelSignal::Resume` from the exact same sender — which is entirely optional and unenforceable, since it's driven by the counterparty's own collator/runtime logic, not a protocol requirement. There is no timeout, retry limit, or block-height-based auto-resume implemented in the pallet, and no permissionless extrinsic exposed to force-resume a specific outbound channel; recovering requires relay-chain/governance-level HRMP channel manipulation (closing/reopening the channel), which is an admin-only action, not something reachable by ordinary users.

### Impact Explanation
A connected sibling parachain that behaves adversarially (or even just buggy, since no cryptographic distinction exists between "legitimate backpressure signal" and "malicious repeated Suspend without Resume") can permanently freeze all outbound XCM traffic — including asset transfers — from the victim chain to that specific sibling. Legitimate users of the victim chain who wish to send assets/messages to that destination parachain have no recourse; their messages queue indefinitely behind the suspended channel with no user-triggerable unblock mechanism.

### Likelihood Explanation
Preconditions are minimal and match the threat model given: the attacker only needs an already-open HRMP channel with the victim chain (a normal, common parachain relationship) and the ability to author its own outbound XCMP page content — no relay-chain privilege, no compromise of the victim chain, and no `ControllerOrigin` on the victim side is required. A single malicious/misconfigured signal page suffices; repeating it is trivial and requires no special timing. This is fully within reach of any sibling chain team or even a compromised/rogue collator set on that sibling.

### Recommendation
Add a bounded, permissionless (or at least chain-local, non-relay-governance) recovery mechanism for outbound channel suspension triggered by remote signals: e.g., an automatic timeout that reverts `OutboundState::Suspended` back to `Ok` after N blocks without a `Resume`, and/or expose a local (non-`ControllerOrigin`-gated, or at minimum lower-privilege) mechanism to clear a stale remotely-triggered suspension. At minimum, track the block at which `suspend_channel` set the suspended state and enforce a maximum suspension duration in `on_idle`/`on_initialize` before allowing outbound traffic to resume regardless of whether a `Resume` signal arrives.

### Proof of Concept
Extend `cumulus/pallets/xcmp-queue/src/tests.rs::handling_signals_works`:
1. Call `XcmpQueue::handle_xcmp_messages(vec![(SIBLING_PARA, 1, (XcmpMessageFormat::Signals, ChannelSignal::Suspend).encode())].into_iter(), &mut WeightMeter::new())`.
2. Assert `OutboundXcmpStatus::<Test>::get()` shows `SIBLING_PARA` entry with `state == OutboundState::Suspended`.
3. Advance the block number by an arbitrarily large number of blocks (e.g., `run_to_block(100_000)`), without ever sending `ChannelSignal::Resume`.
4. Attempt to enqueue an outbound XCM to `SIBLING_PARA` (e.g., via `XcmpQueue::send_xcm` or `take_outbound_messages`) and assert it is *not* delivered/serviced.
5. Assert there is no state transition back to `OutboundState::Ok` and no extrinsic reachable without `ControllerOrigin` that can clear it — proving the suspension is permanent absent governance/relay-level intervention.

### Citations

**File:** cumulus/pallets/xcmp-queue/src/lib.rs (L1-1)
```rust
// Copyright (C) Parity Technologies (UK) Ltd.
```
