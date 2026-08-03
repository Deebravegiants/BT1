[1](#0-0) [2](#0-1)

### Citations

**File:** types/src/on_chain_config/aptos_features.rs (L107-109)
```rust
    FEDERATED_KEYLESS = 77,
    TRANSACTION_SIMULATION_ENHANCEMENT = 78,
    COLLECTION_OWNER = 79,
```

**File:** types/src/on_chain_config/aptos_features.rs (L418-423)
```rust
    pub fn is_enabled(&self, flag: FeatureFlag) -> bool {
        let val = flag as u64;
        let byte_index = (val / 8) as usize;
        let bit_mask = 1 << (val % 8);
        byte_index < self.features.len() && (self.features[byte_index] & bit_mask != 0)
    }
```
