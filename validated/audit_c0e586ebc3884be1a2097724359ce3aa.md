[1](#0-0)

### Citations

**File:** polkadot/runtime/parachains/src/hrmp.rs (L17-39)
```rust
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
