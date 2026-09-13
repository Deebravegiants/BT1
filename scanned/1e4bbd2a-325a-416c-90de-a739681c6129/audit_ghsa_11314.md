# [M] kora-lib: Unrecognized Instruction Types Create Empty Stubs That Bypass Fee Payer Policy

## Summary
Severity: Medium
Advisory: GHSA-x442-m7cc-hr92
CWE: CWE-693
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-x442-m7cc-hr92
Type: github-advisory

## Affected
- crates.io: `kora-lib` — affected >=0 <2.0.5

## Details
## Summary

When inner CPI instructions use instruction types not recognized by Kora's parser (including Token-2022 extension instructions like `ConfidentialTransfer`, `TransferFeeExtension::WithdrawWithheldTokens`, etc.), they are reconstructed as stub instructions with empty accounts and empty data. These stubs fail deserialization during fee payer policy validation and are silently skipped, meaning any fee payer usage within those instructions goes completely unchecked.

## Severity

**Medium**

## Affected Component

- **File:** `crates/lib/src/transaction/instruction_util.rs`
- **Functions:** `reconstruct_system_instruction()`, `reconstruct_spl_token_instruction()`
- **Lines:** 750–753, 1187–1189

## Root Cause

The instruction reconstruction functions have a catch-all `_ =>` arm for unrecognized instruction types that creates a stub `CompiledInstruction` with the correct `program_id_index` but **empty `accounts` and empty `data`**. When this stub reaches the fee payer policy parsing (`parse_system_instructions` / `parse_token_instructions`), deserialization of empty data fails. The parsing functions also have a catch-all `_ => {}` that silently skips the failed instruction. The result: the instruction exists in `all_instructions` (so program allowlist checks pass), but fee payer policy is never enforced on it.

## Vulnerable Code

### Stub Creation

```rust
// crates/lib/src/transaction/instruction_util.rs:750-753
// System program — unrecognized instruction type:
_ => {
    log::error!("Unsupported system instruction type: {}", instruction_type);
    Ok(Self::build_default_compiled_instruction(program_id_index))
}

// crates/lib/src/transaction/instruction_util.rs:1187-1189
// SPL Token program — unrecognized instruction type:
_ => {
    log::error!("Unsupported token instruction type: {}", instruction_type);
    Ok(Self::build_default_compiled_instruction(program_id_index))
}
```

The stub builder:
```rust
pub fn build_default_compiled_instruction(program_id_index: u8) -> CompiledInstruction {
    CompiledInstruction {
        program_id_index,
        accounts: vec![],  // <-- No accounts
        data: vec![],       // <-- No data
    }
}
```

### Silent Skip During Policy Parsing

```rust
// In parse_system_instructions:
if let Ok(system_instruction) = bincode::deserialize::<SystemInstruction>(&instruction.data) {
    match system_instruction {
        // ... known types handled ...
        _ => {}  // <-- Unrecognized: silently skipped
    }
}
// If deserialize fails (empty data), the entire `if let Ok` block is skipped.
// The instruction is not added to any policy check map.

// In parse_token_instructions:
if let Ok(token_instruction) = TokenInstruction::unpack(&instruction.data) {
    match token_instruction {
        // ... known types handled ...
        _ => {}  // <-- Unrecognized: silently skipped
    }
}
// Same: empty data causes unpack to fail, instruction completely invisible to policy.
```

## Proof of Concept

### Affected Token-2022 Extension Instructions

The following Token-2022 extension instruction types are NOT handled by Kora's parser and would produce empty stubs:

| Extension | Instruction | Risk if Fee Payer is Authority |
|-----------|------------|-------------------------------|
| `TransferFeeExtension` | `WithdrawWithheldTokensFromMint` | Fee payer as withdraw authority can drain withheld fees |
| `TransferFeeExtension` | `WithdrawWithheldTokensFromAccounts` | Same |
| `TransferFeeExtension` | `HarvestWithheldTokensToMint` | Fee collection manipulation |
| `ConfidentialTransfer` | `Transfer` | Hidden transfer amounts bypass fee tracking |
| `ConfidentialTransfer` | `Withdraw` | Hidden withdrawals |
| `InterestBearingMint` | `UpdateRate` | Fee payer as rate authority can manipulate interest |
| `TransferHook` | `Execute` | Arbitrary hook execution |
| `GroupMemberPointer` | `Update` | Metadata manipulation |
| `MetadataPointer` | `Update` | Metadata manipulation |
| `PermanentDelegate` | `Transfer` (via delegate) | Delegate-based unauthorized transfers |

### Code Path Trace

```
1. Transaction contains an inner CPI instruction:
   Program: Token-2022
   Type: "withdrawWithheldTokensFromMint" (TransferFeeExtension)
   Accounts: [fee_payer (as withdraw_withheld_authority), mint, destination]

2. RPC returns this as a Parsed inner instruction

3. reconstruct_spl_token_instruction() is called:
   - instruction_type = "withdrawWithheldTokensFromMint"
   - No match in the known types (transfer, transferChecked, burn, etc.)
   - Falls through to _ => arm
   - Returns: CompiledInstruction { program_id_index, accounts: [], data: [] }

4. Stub is added to all_instructions
   → validate_programs() sees Token-2022 program ID → PASS (allowed)
   → validate_disallowed_accounts() sees no accounts in the stub → PASS

5. parse_token_instructions() processes the stub:
   - TokenInstruction::unpack(&[]) → Err (empty data)
   - if let Ok(...) block skipped entirely
   - Instruction not added to any ParsedSPLInstructionType map

6. validate_fee_payer_usage() iterates parsed SPL instructions:
   - No entry for "withdrawWithheldTokensFromMint"
   - Fee payer's usage as withdraw_withheld_authority is NEVER checked

7. Transaction is signed by Kora

8. On-chain: fee_payer (as withdraw authority) withdraws withheld
   transfer fees from the mint to attacker's account
```

### Verifiable Test

```rust
#[test]
fn test_unrecognized_instruction_produces_empty_stub() {
    // Simulate what happens for an unrecognized Token-2022 instruction
    let program_id_index: u8 = 3; // Token-2022 at index 3

    // This is what the catch-all arm produces:
    let stub = IxUtils::build_default_compiled_instruction(program_id_index);

    assert_eq!(stub.accounts.len(), 0);  // No accounts
    assert_eq!(stub.data.len(), 0);      // No data

    // Attempt to parse it:
    let result = TokenInstruction::unpack(&stub.data);
    assert!(result.is_err());  // Cannot parse empty data

    // Therefore: fee payer policy is never applied to this instruction
    // The fee payer could be the withdraw_withheld_authority in the
    // REAL instruction, but the stub has zero accounts — invisible.
}
```

## Impact

- **Fee Payer Policy Bypass:** Token-2022 extension instructions that use the fee payer as an authority are invisible to policy enforcement.
- **Forward-Looking Risk:** As Solana and SPL Token-2022 add new instruction types, they will automatically bypass all fee payer policy checks in Kora.
- **Precondition:** Requires the fee payer to hold some authority role (e.g., `withdraw_withheld_authority`, `permanent_delegate`) for Token-2022 accounts. This is unlikely in typical deployments but possible in misconfigured setups.

## Recommendation

Reject transactions containing inner instructions with unrecognized types (fail-secure):

```rust
// In reconstruct_system_instruction:
_ => {
    return Err(KoraError::InvalidTransaction(format!(
        "Unrecognized system instruction type '{}' in CPI — \
         cannot validate fee payer policy. Transaction rejected.",
        instruction_type
    )));
}

// In reconstruct_spl_token_instruction:
_ => {
    return Err(KoraError::InvalidTransaction(format!(
        "Unrecognized SPL Token instruction type '{}' in CPI — \
         cannot validate fee payer policy. Transaction rejected.",
        instruction_type
    )));
}
```

Alternatively, maintain a list of known-safe instruction types that don't involve authority checks, and only reject truly unknown types.

## References

- `crates/lib/src/transaction/instruction_util.rs:750-753` — system instruction catch-all
- `crates/lib/src/transaction/instruction_util.rs:1187-1189` — SPL token instruction catch-all
- `crates/lib/src/transaction/instruction_util.rs:316-319` — `build_default_compiled_instruction`
- [SPL Token-2022 instruction types](https://github.com/solana-labs/solana-program-library/tree/master/token/program-2022/src/extension) — full list of extension instructions

## References
- https://github.com/solana-foundation/kora/security/advisories/GHSA-x442-m7cc-hr92
- https://github.com/solana-foundation/kora
