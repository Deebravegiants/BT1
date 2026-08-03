[1](#0-0) [2](#0-1)

### Citations

**File:** aptos-move/aptos-vm/src/transaction_validation_versioned.rs (L128-131)
```rust
    let sender = serialized_signers.sender();
    let fee_payer = serialized_signers
        .fee_payer()
        .unwrap_or_else(|| serialized_signers.sender());
```

**File:** aptos-move/aptos-vm/src/transaction_validation_versioned.rs (L216-219)
```rust
    let sender = serialized_signers.sender();
    let fee_payer = serialized_signers
        .fee_payer()
        .unwrap_or_else(|| serialized_signers.sender());
```
