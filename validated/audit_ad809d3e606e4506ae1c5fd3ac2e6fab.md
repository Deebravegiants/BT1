[1](#0-0) [2](#0-1)

### Citations

**File:** aptos-move/framework/aptos-framework/sources/account/account.move (L60-69)
```text
    /// Resource representing an account.
    struct Account has key, store {
        authentication_key: vector<u8>,
        sequence_number: u64,
        guid_creation_num: u64,
        coin_register_events: EventHandle<CoinRegisterEvent>,
        key_rotation_events: EventHandle<KeyRotationEvent>,
        rotation_capability_offer: CapabilityOffer<RotationCapability>,
        signer_capability_offer: CapabilityOffer<SignerCapability>,
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L38-60)
```text
module aptos_framework::multisig_account {
    use aptos_framework::account::{Self, SignerCapability, new_event_handle, create_resource_address};
    use aptos_framework::aptos_coin::AptosCoin;
    use aptos_framework::chain_id;
    use aptos_framework::create_signer::create_signer;
    use aptos_framework::coin;
    use aptos_framework::event::{EventHandle, emit};
    use aptos_framework::timestamp::now_seconds;
    use aptos_std::simple_map::{Self, SimpleMap};
    use aptos_std::table::{Self, Table};
    use std::bcs::to_bytes;
    use std::features;
    use std::error;
    use std::hash::sha3_256;
    use std::option::{Self, Option};
    use std::signer::address_of;
    use std::string::String;
    use std::vector;

    /// The salt used to create a resource account during multisig account creation.
    /// This is used to avoid conflicts with other modules that also create resource accounts with the same owner
    /// account.
    const DOMAIN_SEPARATOR: vector<u8> = b"aptos_framework::multisig_account";
```
