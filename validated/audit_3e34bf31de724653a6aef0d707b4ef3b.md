[1](#0-0)

### Citations

**File:** types/src/account_config/events/mint_token_event.rs (L15-53)
```rust
#[derive(Debug, Deserialize, Serialize)]
pub struct MintTokenEvent {
    id: TokenDataId,
    amount: u64,
}

impl MintTokenEvent {
    pub fn new(id: TokenDataId, amount: u64) -> Self {
        Self { id, amount }
    }

    pub fn try_from_bytes(bytes: &[u8]) -> Result<Self> {
        bcs::from_bytes(bytes).map_err(Into::into)
    }

    pub fn id(&self) -> &TokenDataId {
        &self.id
    }

    pub fn amount(&self) -> u64 {
        self.amount
    }
}

impl MoveStructType for MintTokenEvent {
    const MODULE_NAME: &'static IdentStr = ident_str!("token");
    const STRUCT_NAME: &'static IdentStr = ident_str!("MintTokenEvent");
}

impl MoveEventV1Type for MintTokenEvent {}

pub static MINT_TOKEN_EVENT_TYPE: Lazy<TypeTag> = Lazy::new(|| {
    TypeTag::Struct(Box::new(StructTag {
        address: TOKEN_ADDRESS,
        module: ident_str!("token").to_owned(),
        name: ident_str!("MintTokenEvent").to_owned(),
        type_args: vec![],
    }))
});
```
