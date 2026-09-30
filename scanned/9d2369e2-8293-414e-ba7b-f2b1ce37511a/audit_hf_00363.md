# [H] Quote pools are expected to have same base

## Summary
Severity: High
Contest weight: 0.2949
Dataset id: 1737
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The missing constraint that enforces quote pools should have the same base and quote token will cause swap fees to be deducted from non-quote pools.
By design, quote pools are pools with the same base and quote token. The
// record fee into account
woopool_quote.sub_reserve(swap_fee).unwrap();
woopool_quote.add_unclaimed_fee(swap_fee).unwrap();
In swap.rs:79-84, there is no constraint that enforces that the pool used as the quote pool has the same base token and quote token.
```rust
#[account(mut,
has_one = wooconfig,
constraint = woopool_quote.token_mint == woopool_from.quote_token_mint,
constraint = woopool_quote.authority == woopool_from.authority,
)]
woopool_quote: Box<Account<'info, WooPool>>,
```
This means that non-quote pools can be used as quote pools during swaps and swap fees will be deducted from these.
// record fee into account
woopool_quote.sub_reserve(swap_fee).unwrap();
woopool_quote.add_unclaimed_fee(swap_fee).unwrap();
Internal pre-conditions
None
External pre-conditions
None
Attack Path
1. Anyone can execute swaps by invoking the swap instruction and passing a non-quote pool as a woopool_quote. The constraints will allow it as long as the woopool_quote's base token is the same as the woopool_from's quote token and the pools have the same owners.
Swap fees can be deducted from non-quote pools instead of quote pools only.

## Recommendation
Consider adding a constraint that enforces that the quote pool is a pool with the same base and quote token.
