[1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** third_party/move/move-binary-format/src/access.rs (L77-81)
```rust
    fn struct_variant_handle_at(&self, idx: StructVariantHandleIndex) -> &StructVariantHandle {
        let handle = &self.as_module().struct_variant_handles[idx.into_index()];
        debug_assert!(handle.struct_index.into_index() < self.as_module().struct_defs.len()); // invariant
        handle
    }
```

**File:** third_party/move/move-binary-format/src/check_bounds.rs (L1-1)
```rust
// Parts of the file are Copyright (c) The Diem Core Contributors
```

**File:** third_party/move/move-bytecode-verifier/src/struct_api_checker.rs (L1-1)
```rust
// Parts of the file are Copyright (c) The Diem Core Contributors
```
