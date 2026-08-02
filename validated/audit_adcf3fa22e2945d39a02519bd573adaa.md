[1](#0-0)

### Citations

**File:** aptos-move/aptos-native-interface/src/builder.rs (L138-141)
```rust
                    } => {
                        if let Some(abort_message) = abort_message.as_ref() {
                            check_abort_message_limit(abort_message.len())?;
                        }
```
