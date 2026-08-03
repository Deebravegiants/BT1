[1](#0-0) [2](#0-1)

### Citations

**File:** aptos-move/block-executor/src/explicit_sync_wrapper.rs (L15-22)
```rust
/// ExplicitSyncWrapper is meant to be used in parallel algorithms
/// where we can prove that there will be no concurrent access to the
/// underlying object (or its elements).  Use with caution - only when
/// the safety can be proven.
#[derive(Debug)]
pub struct ExplicitSyncWrapper<T> {
    value: UnsafeCell<T>,
}
```

**File:** aptos-move/block-executor/src/explicit_sync_wrapper.rs (L60-62)
```rust
    pub fn dereference_mut<'a>(&self) -> &'a mut T {
        unsafe { &mut *self.value.get() }
    }
```
