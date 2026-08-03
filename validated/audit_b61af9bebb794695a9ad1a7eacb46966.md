[1](#0-0) [2](#0-1)

### Citations

**File:** types/src/proof/definition.rs (L6-9)
```rust
use super::{
    accumulator::InMemoryAccumulator, position::Position, verify_transaction_info,
    MerkleTreeInternalNode, SparseMerkleInternalNode, SparseMerkleLeafNode,
};
```

**File:** types/src/proof/definition.rs (L18-24)
```rust
use aptos_crypto::{
    hash::{
        CryptoHash, CryptoHasher, EventAccumulatorHasher, TransactionAccumulatorHasher,
        SPARSE_MERKLE_PLACEHOLDER_HASH,
    },
    HashValue,
};
```
