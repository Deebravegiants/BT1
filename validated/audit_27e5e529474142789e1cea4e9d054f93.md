[1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** types/src/account_config/resources/fungible_store.rs (L4-18)
```rust
use super::aggregator::AggregatorResource;
use crate::account_address::create_derived_object_address;
use move_core_types::{
    account_address::AccountAddress,
    ident_str,
    identifier::IdentStr,
    move_resource::{MoveResource, MoveStructType},
};
#[cfg(any(test, feature = "fuzzing"))]
use proptest_derive::Arbitrary;
use serde::{Deserialize, Serialize};

pub fn primary_apt_store(address: AccountAddress) -> AccountAddress {
    create_derived_object_address(address, AccountAddress::TEN)
}
```

**File:** aptos-move/framework/aptos-framework/sources/primary_fungible_store.move (L1-14)
```text
/// This module provides a way for creators of fungible assets to enable support for creating primary (deterministic)
/// stores for their users. This is useful for assets that are meant to be used as a currency, as it allows users to
/// easily create a store for their account and deposit/withdraw/transfer fungible assets to/from it.
///
/// The transfer flow works as below:
/// 1. The sender calls `transfer` on the fungible asset metadata object to transfer `amount` of fungible asset to
///   `recipient`.
/// 2. The fungible asset metadata object calls `ensure_primary_store_exists` to ensure that both the sender's and the
/// recipient's primary stores exist. If either doesn't, it will be created.
/// 3. The fungible asset metadata object calls `withdraw` on the sender's primary store to withdraw `amount` of
/// fungible asset from it. This emits a withdraw event.
/// 4. The fungible asset metadata object calls `deposit` on the recipient's primary store to deposit `amount` of
/// fungible asset to it. This emits an deposit event.
module aptos_framework::primary_fungible_store {
```

**File:** api/src/accounts.rs (L20-28)
```rust
use aptos_sdk::types::{get_paired_fa_metadata_address, get_paired_fa_primary_store_address};
use aptos_types::{
    account_config::{
        AccountResource, CoinStoreResourceUntyped, ConcurrentFungibleBalanceResource,
        FungibleStoreResource, ObjectGroupResource,
    },
    event::{EventHandle, EventKey},
    state_store::state_key::StateKey,
};
```
