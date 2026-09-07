# [M] kora-lib: Token-2022 Transfer Fee Not Deducted During Payment Verification

## Summary
Severity: Medium
Advisory: GHSA-725g-w329-g7qr
Ecosystem: crates.io
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-725g-w329-g7qr
Type: github-advisory

## Affected
- crates.io: `kora-lib` — affected >=0 <2.0.5

## Details
## Summary

When a user pays transaction fees using a Token-2022 token with a `TransferFeeConfig` extension, Kora's `verify_token_payment()` credits the full raw transfer `amount` as the payment value. However, the on-chain SPL Token-2022 program withholds a portion of that amount as a transfer fee, so the paymaster's destination account only receives `amount - transfer_fee`. This means the paymaster consistently credits more value than it actually receives, resulting in systematic financial loss.

## Severity

**High**

## Affected Component

- **File:** `crates/lib/src/token/token.rs`
- **Function:** `verify_token_payment()`
- **Lines:** 529–654 (specifically 633–639)

## Root Cause

In `verify_token_payment()`, the `amount` extracted from the parsed SPL transfer instruction is the **pre-fee** amount (what the sender specifies in the `transfer_checked` instruction). The function passes this raw amount to `calculate_token_value_in_lamports()` to determine how many lamports the payment is worth. It never subtracts the Token-2022 transfer fee.

The fee estimation path (`fee.rs:analyze_payment_instructions`) correctly accounts for transfer fees by calculating them and adding them to the total fee. But the verification path does not perform the inverse subtraction, creating an asymmetry.

## Vulnerable Code

```rust
// crates/lib/src/token/token.rs:529-654
pub async fn verify_token_payment(
    transaction_resolved: &mut VersionedTransactionResolved,
    rpc_client: &RpcClient,
    required_lamports: u64,
    expected_destination_owner: &Pubkey,
) -> Result<bool, KoraError> {
    let config = get_config()?;
    let mut total_lamport_value = 0u64;

    // ...

    for instruction in transaction_resolved
        .get_or_parse_spl_instructions()?
        .get(&ParsedSPLInstructionType::SplTokenTransfer)
        .unwrap_or(&vec![])
    {
        if let ParsedSPLInstructionData::SplTokenTransfer {
            source_address,
            destination_address,
            mint,
            amount,      // <-- This is the PRE-FEE amount from the instruction
            is_2022,
            ..
        } = instruction
        {
            // ... destination validation ...

            // LINE 633-639: Uses raw *amount without deducting transfer fee
            let lamport_value = TokenUtil::calculate_token_value_in_lamports(
                *amount,        // <-- BUG: Should be (amount - transfer_fee)
                &token_mint,
                config.validation.price_source.clone(),
                rpc_client,
            )
            .await?;

            total_lamport_value = total_lamport_value
                .checked_add(lamport_value)
                .ok_or_else(|| {
                    KoraError::ValidationError("Payment accumulation overflow".to_string())
                })?;
        }
    }

    Ok(total_lamport_value >= required_lamports)
}
```

For comparison, the transfer fee calculation exists elsewhere in the codebase and is used during fee estimation:

```rust
// crates/lib/src/token/spl_token_2022.rs:165-198
pub fn calculate_transfer_fee(
    &self,
    amount: u64,
    current_epoch: u64,
) -> Result<Option<u64>, KoraError> {
    if let Some(fee_config) = self.get_transfer_fee() {
        let transfer_fee = if current_epoch >= u64::from(fee_config.newer_transfer_fee.epoch) {
            &fee_config.newer_transfer_fee
        } else {
            &fee_config.older_transfer_fee
        };
        let basis_points = u16::from(transfer_fee.transfer_fee_basis_points);
        let maximum_fee = u64::from(transfer_fee.maximum_fee);
        let fee_amount = (amount as u128)
            .checked_mul(basis_points as u128)
            .and_then(|product| product.checked_div(10_000))
            // ...
        Ok(Some(std::cmp::min(fee_amount, maximum_fee)))
    } else {
        Ok(None)
    }
}
```

This function exists but is **never called** in `verify_token_payment()`.

## Proof of Concept

### Arithmetic Demonstration

Given:
- Token-2022 token with 5% transfer fee (500 basis points), whitelisted in `allowed_spl_paid_tokens`
- Transaction fee cost: 5000 lamports equivalent
- Token price: 1 token = 5 lamports

**What should happen:**
- User needs to pay 5000 lamports worth → 1000 tokens
- Transfer fee on 1000 tokens at 5% = 50 tokens
- Paymaster destination receives: 1000 - 50 = 950 tokens (worth 4750 lamports)
- User should be required to pay MORE to cover the fee

**What actually happens:**
- User sends `transfer_checked` for `amount = 1000` tokens
- `verify_token_payment()` calculates: 1000 tokens * 5 lamports/token = 5000 lamports
- 5000 >= 5000 required → **payment verified as sufficient**
- But paymaster only received 950 tokens (worth 4750 lamports)
- **Paymaster lost 250 lamports on this transaction**

**Over 1000 transactions:** Paymaster loses 250,000 lamports (0.25 SOL)

### Runnable Test (using existing test infrastructure)

```rust
#[tokio::test]
async fn test_token2022_transfer_fee_not_deducted_in_verification() {
    // Setup: Token-2022 mint with 10% transfer fee (1000 bps)
    let transfer_fee_config = create_transfer_fee_config(
        1000,      // 10% basis points
        u64::MAX,  // no maximum fee cap
    );

    let mint_pubkey = Pubkey::new_unique();
    let mint_account = MintAccountMockBuilder::new()
        .with_decimals(6)
        .with_supply(1_000_000_000_000)
        .with_extension(ExtensionType::TransferFeeConfig)
        .build_token2022();

    // User sends transfer_checked for 1,000,000 tokens (1 token at 6 decimals)
    let transfer_amount: u64 = 1_000_000;

    // What verify_token_payment credits:
    let credited_amount = transfer_amount;  // = 1,000,000

    // What the paymaster actually receives (after 10% on-chain fee):
    let actual_received = transfer_amount - (transfer_amount * 1000 / 10000);  // = 900,000

    // BUG: credited_amount (1,000,000) > actual_received (900,000)
    // Paymaster is credited 11.1% MORE than it actually receives
    assert!(credited_amount > actual_received);
    assert_eq!(credited_amount - actual_received, 100_000); // 100,000 token units lost

    // The financial loss per transaction = 10% of the payment amount
    // This is NOT a rounding error — it is a full percentage-based loss
}
```

## Impact

- **Systematic Financial Loss:** The paymaster consistently credits more token value than it receives for every transaction paid with a transfer-fee-bearing Token-2022 token.
- **Loss Scale:** Proportional to `transfer_fee_basis_points / 10000 * payment_amount` per transaction. For a token with 5% fee and 100 transactions/day at $1 each, that is $5/day or $1,825/year in losses.
- **Precondition:** Requires a Token-2022 token with `TransferFeeConfig` extension to be whitelisted in `allowed_spl_paid_tokens`. The existing test infrastructure already creates such tokens (`TestAccountSetup::create_usdc_mint_2022()` with 100 bps / 1% fee).

## Recommendation

Deduct the Token-2022 transfer fee before calculating the lamport value of the payment:

```rust
// In verify_token_payment(), after extracting amount:
let effective_amount = if *is_2022 {
    // Fetch the mint to check for TransferFeeConfig
    let mint_account = CacheUtil::get_account(
        rpc_client,
        &token_mint,
        false,
    ).await?;
    let mint_info = Token2022MintInfo::from_account_data(&mint_account.data)?;

    if let Ok(Some(fee)) = mint_info.calculate_transfer_fee(
        *amount,
        rpc_client.get_epoch_info().await?.epoch,
    ) {
        amount.saturating_sub(fee)
    } else {
        *amount
    }
} else {
    *amount
};

let lamport_value = TokenUtil::calculate_token_value_in_lamports(
    effective_amount,  // Use post-fee amount
    &token_mint,
    config.validation.price_source.clone(),
    rpc_client,
)
.await?;
```

## References

- `crates/lib/src/token/token.rs:529-654` — `verify_token_payment()` using raw amount
- `crates/lib/src/token/spl_token_2022.rs:165-198` — `calculate_transfer_fee()` (exists but not called in verification)
- `crates/lib/src/fee/fee.rs:174-204` — `analyze_payment_instructions()` (correctly accounts for transfer fee in estimation)
- SPL Token-2022 specification: transfer fees are deducted from the transfer amount by the on-chain program

## References
- https://github.com/solana-foundation/kora/security/advisories/GHSA-725g-w329-g7qr
- https://github.com/solana-foundation/kora/commit/8cbd8217ee505e6b37c63ef835ff095cfa8ab318
- https://github.com/solana-foundation/kora
