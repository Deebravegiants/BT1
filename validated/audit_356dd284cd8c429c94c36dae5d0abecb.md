No vulnerability found for this question.

**Analysis:** The premise is incorrect. In the in-memory representation, there is no metadata-less `Deletion` variant to be confused with a metadata-bearing one. `BaseStateOp` (which backs `WriteOp`) defines deletion as a single variant that always carries the metadata: `Deletion(StateValueMetadata)` [1](#0-0) . The split into `Deletion` vs `DeletionWithMetadata` only exists in `PersistedWriteOp`, purely as a wire-format optimization to avoid serializing an empty/`None` metadata byte [2](#0-1) .

`WriteOp::to_persistable` chooses the plain `Deletion` arm only when `self.metadata().clone().into_persistable()` returns `None` (i.e., the metadata truly was empty/legacy), and chooses `DeletionWithMetadata { metadata }` whenever there was real metadata to persist [3](#0-2) . `PersistedWriteOp::into_in_mem_form` reconstructs `WriteOp::deletion(metadata.into_in_mem_form())` from `DeletionWithMetadata`, and `WriteOp::legacy_deletion()` (empty metadata) from plain `Deletion` [4](#0-3) , [5](#0-4) . This round trip is lossless: non-trivial metadata always comes back through `DeletionWithMetadata`, never silently dropped into the plain arm.

Because every downstream consumer that operates on `WriteOp`/`BaseStateOp` (e.g. `metadata()`, `metadata_mut()`, `into_metadata()`) pattern-matches on the single `BaseStateOp::Deletion(meta)` arm and always receives the metadata [6](#0-5) , there is no code path where a consumer can only see a "metadata-less Deletion" while the real metadata silently exists elsewhere. The only place matching on `PersistedWriteOp`'s two-variant split is `into_in_mem_form` itself, which correctly reconstructs the metadata in both cases. No custody-relevant consumer reads `PersistedWriteOp` directly and treats its `Deletion` variant as authoritative for refund/rent ownership — all such logic operates on the reconstructed `WriteOp`, which never loses metadata.

### Citations

**File:** types/src/write_set.rs (L46-63)
```rust
#[derive(Serialize, Deserialize)]
#[serde(rename = "WriteOp")]
pub enum PersistedWriteOp {
    Creation(Bytes),
    Modification(Bytes),
    Deletion,
    CreationWithMetadata {
        data: Bytes,
        metadata: PersistedStateValueMetadata,
    },
    ModificationWithMetadata {
        data: Bytes,
        metadata: PersistedStateValueMetadata,
    },
    DeletionWithMetadata {
        metadata: PersistedStateValueMetadata,
    },
}
```

**File:** types/src/write_set.rs (L65-82)
```rust
impl PersistedWriteOp {
    fn into_in_mem_form(self) -> WriteOp {
        use PersistedWriteOp::*;

        match self {
            Creation(data) => WriteOp::legacy_creation(data),
            Modification(data) => WriteOp::legacy_modification(data),
            Deletion => WriteOp::legacy_deletion(),
            CreationWithMetadata { data, metadata } => {
                WriteOp::creation(data, metadata.into_in_mem_form())
            },
            ModificationWithMetadata { data, metadata } => {
                WriteOp::modification(data, metadata.into_in_mem_form())
            },
            DeletionWithMetadata { metadata } => WriteOp::deletion(metadata.into_in_mem_form()),
        }
    }
}
```

**File:** types/src/write_set.rs (L86-91)
```rust
pub enum BaseStateOp {
    Creation(StateValue),
    Modification(StateValue),
    Deletion(StateValueMetadata),
    MakeHot,
}
```

**File:** types/src/write_set.rs (L133-157)
```rust
    pub fn to_persistable(&self) -> PersistedWriteOp {
        use PersistedWriteOp::*;

        let metadata = self.metadata().clone().into_persistable();
        match metadata {
            None => match &self.0 {
                BaseStateOp::Creation(v) => Creation(v.bytes().clone()),
                BaseStateOp::Modification(v) => Modification(v.bytes().clone()),
                BaseStateOp::Deletion { .. } => Deletion,
                BaseStateOp::MakeHot => unreachable!("malformed write op"),
            },
            Some(metadata) => match &self.0 {
                BaseStateOp::Creation(v) => CreationWithMetadata {
                    data: v.bytes().clone(),
                    metadata,
                },
                BaseStateOp::Modification(v) => ModificationWithMetadata {
                    data: v.bytes().clone(),
                    metadata,
                },
                BaseStateOp::Deletion { .. } => DeletionWithMetadata { metadata },
                BaseStateOp::MakeHot => unreachable!("malformed write op"),
            },
        }
    }
```

**File:** types/src/write_set.rs (L232-260)
```rust
    pub fn metadata(&self) -> &StateValueMetadata {
        use BaseStateOp::*;

        match &self.0 {
            Creation(v) | Modification(v) => v.metadata(),
            Deletion(meta) => meta,
            MakeHot => unreachable!("malformed write op"),
        }
    }

    pub fn metadata_mut(&mut self) -> &mut StateValueMetadata {
        use BaseStateOp::*;

        match &mut self.0 {
            Creation(v) | Modification(v) => v.metadata_mut(),
            Deletion(meta) => meta,
            MakeHot => unreachable!("malformed write op"),
        }
    }

    pub fn into_metadata(self) -> StateValueMetadata {
        use BaseStateOp::*;

        match self.0 {
            Creation(v) | Modification(v) => v.into_metadata(),
            Deletion(meta) => meta,
            MakeHot => unreachable!("malformed write op"),
        }
    }
```

**File:** types/src/write_set.rs (L278-292)
```rust
    pub fn deletion(metadata: StateValueMetadata) -> Self {
        Self(BaseStateOp::Deletion(metadata))
    }

    pub fn legacy_creation(data: Bytes) -> Self {
        Self(BaseStateOp::Creation(StateValue::new_legacy(data)))
    }

    pub fn legacy_modification(data: Bytes) -> Self {
        Self(BaseStateOp::Modification(StateValue::new_legacy(data)))
    }

    pub fn legacy_deletion() -> Self {
        Self(BaseStateOp::Deletion(StateValueMetadata::none()))
    }
```
