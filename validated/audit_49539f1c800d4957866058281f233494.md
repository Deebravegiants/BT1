[1](#0-0)

### Citations

**File:** third_party/move/move-vm/types/src/views.rs (L36-48)
```rust
    fn legacy_abstract_memory_size(&self) -> AbstractMemorySize {
        /// The size in bytes for a non-string or address constant on the stack
        const LEGACY_CONST_SIZE: AbstractMemorySize = AbstractMemorySize::new(16);

        /// The size in bytes for a reference on the stack
        const LEGACY_REFERENCE_SIZE: AbstractMemorySize = AbstractMemorySize::new(8);

        /// The size of a struct in bytes
        const LEGACY_STRUCT_SIZE: AbstractMemorySize = AbstractMemorySize::new(2);

        /// The size of a closure in bytes
        const LEGACY_CLOSURE_SIZE: AbstractMemorySize = AbstractMemorySize::new(6);

```
