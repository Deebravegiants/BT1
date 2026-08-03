No vulnerability found for this question.

**Reasoning:**

`coin::register<CoinType>` requires a `&signer` for the target account: [1](#0-0) . Producing a signer for a resource account requires either the account's private key (rotated to `0x0` / zeroed out once the capability is retrieved) or possession of the `SignerCapability` itself via `account::create_signer_with_capability` [2](#0-1) . After `retrieve_resource_account_cap` is called, the `SignerCapability` is removed from the `Container` and returned to the caller (typically stored inside the calling module's state, e.g. `ModuleData`), and the resource account's auth key is rotated to `ZERO_AUTH_KEY`, permanently locking direct key-based access [3](#0-2) .

For an unprivileged attacker to call `coin::register<CoinType>` "against" that resource account, they would need to supply a `signer` for that address — which requires them to already hold the `SignerCapability` (a privileged asset) or the zeroed auth key (unusable). There is no entrypoint that lets an arbitrary caller produce a resource-account signer without already possessing the capability, so this does not qualify as an "unprivileged" path per the review's decision standard.

Additionally, `CoinRegisterEvent`/`CoinRegister` is a pure telemetry event emitted by `account::register_coin` [4](#0-3)  and by the corresponding Rust-side struct definition [5](#0-4) . It carries no capability, ownership, or freeze-state information — it only signals that a `CoinStore`/registration occurred. It cannot be used on-chain to attest continued possession of a `SignerCapability`, and any external "custody dashboard" that infers capability continuity from this event is making an incorrect assumption about off-chain tooling, not exploiting an on-chain custody boundary. This falls outside "Aptos production custody logic" and does not change who can own, move, mint, burn, freeze, upgrade, or recover value on-chain, so it fails the Custody Impact Gate.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/coin.move (L1127-1133)
```text
    public fun register<CoinType>(account: &signer) {
        let account_addr = signer::address_of(account);
        // Short-circuit and do nothing if account is already registered for CoinType.
        if (is_account_registered<CoinType>(account_addr)) { return };

        account::register_coin<CoinType>(account_addr);
    }
```

**File:** aptos-move/framework/aptos-framework/sources/account/account.move (L1244-1251)
```text
    public(friend) fun register_coin<CoinType>(account_addr: address) {
        event::emit(
            CoinRegister {
                account: account_addr,
                type_info: type_info::type_of<CoinType>(),
            },
        );
    }
```

**File:** aptos-move/framework/aptos-framework/sources/account/account.move (L1273-1276)
```text
    public fun create_signer_with_capability(capability: &SignerCapability): signer {
        let addr = &capability.account;
        create_signer(*addr)
    }
```

**File:** aptos-move/framework/aptos-framework/sources/resource_account.move (L168-196)
```text
    public fun retrieve_resource_account_cap(
        resource: &signer, source_addr: address
    ): account::SignerCapability acquires Container {
        assert!(
            exists<Container>(source_addr),
            error::not_found(ECONTAINER_NOT_PUBLISHED)
        );

        let resource_addr = signer::address_of(resource);
        let (resource_signer_cap, empty_container) = {
            let container = borrow_global_mut<Container>(source_addr);
            assert!(
                container.store.contains_key(&resource_addr),
                error::invalid_argument(EUNAUTHORIZED_NOT_OWNER)
            );
            let (_resource_addr, signer_cap) =
                container.store.remove(&resource_addr);
            (signer_cap, container.store.length() == 0)
        };

        if (empty_container) {
            let container = move_from<Container>(source_addr);
            let Container { store } = container;
            store.destroy_empty();
        };

        account::rotate_authentication_key_internal(resource, ZERO_AUTH_KEY);
        resource_signer_cap
    }
```

**File:** types/src/account_config/events/coin_register_event.rs (L15-33)
```rust
#[derive(Debug, Serialize, Deserialize)]
pub struct CoinRegisterEvent {
    type_info: TypeInfoResource,
}

impl CoinRegisterEvent {
    pub fn new(type_info: TypeInfoResource) -> Self {
        Self { type_info }
    }

    pub fn try_from_bytes(bytes: &[u8]) -> Result<Self> {
        bcs::from_bytes(bytes).map_err(Into::into)
    }
}

impl MoveStructType for CoinRegisterEvent {
    const MODULE_NAME: &'static IdentStr = ident_str!("account");
    const STRUCT_NAME: &'static IdentStr = ident_str!("CoinRegisterEvent");
}
```
