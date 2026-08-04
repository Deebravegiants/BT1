[1](#0-0) [2](#0-1)

### Citations

**File:** cumulus/pallets/xcmp-queue/src/lib.rs (L26-34)
```rust
//! To prevent out of memory errors on the `OutboundXcmpMessages` queue, an exponential fee factor
//! (`DeliveryFeeFactor`) is set, much like the one used in DMP.
//! The fee factor increases whenever the total size of messages in a particular channel passes a
//! threshold. This threshold is defined as a percentage of the maximum total size the channel can
//! have. More concretely, the threshold is `max_total_size` / `THRESHOLD_FACTOR`, where:
//! - `max_total_size` is the maximum size, in bytes, of the channel, not number of messages.
//! It is defined in the channel configuration.
//! - `THRESHOLD_FACTOR` just declares which percentage of the max size is the actual threshold.
//! If it's 2, then the threshold is half of the max size, if it's 4, it's a quarter, and so on.
```

**File:** cumulus/pallets/xcmp-queue/src/lib.rs (L58-83)
```rust
use alloc::{collections::BTreeSet, vec, vec::Vec};
use bitflags::bitflags;
use bounded_collections::{BoundedBTreeSet, BoundedSlice, BoundedVec};
use codec::{Compact, Decode, DecodeLimit, Encode, MaxEncodedLen};
use cumulus_primitives_core::{
	relay_chain::BlockNumber as RelayBlockNumber, ChannelStatus, GetChannelInfo, MessageSendError,
	ParaId, XcmpMessageFormat, XcmpMessageHandler, XcmpMessageSource,
};

use frame_support::{
	defensive, defensive_assert,
	traits::{
		Defensive, DefensiveTruncateFrom, EnqueueMessage, EnsureOrigin, Get, Len, QueueFootprint,
		QueueFootprintQuery, QueuePausedQuery,
	},
	weights::{Weight, WeightMeter},
};
use pallet_message_queue::OnQueueChanged;
use polkadot_runtime_common::xcm_sender::PriceForMessageDelivery;
use polkadot_runtime_parachains::{FeeTracker, GetMinFeeFactor};
use scale_info::TypeInfo;
use sp_core::MAX_POSSIBLE_ALLOCATION;
use sp_runtime::{FixedU128, SaturatedConversion, WeakBoundedVec};
use xcm::{latest::prelude::*, VersionedLocation, VersionedXcm, WrapVersion, MAX_XCM_DECODE_DEPTH};
use xcm_builder::InspectMessageQueues;
use xcm_executor::traits::ConvertOrigin;
```
