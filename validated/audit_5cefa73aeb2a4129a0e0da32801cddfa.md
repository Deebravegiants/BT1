### Title
Attacker permanently blocks permissionless bad-debt cleanup by topping up an insolvent account's collateral above the $5 dust threshold - (contracts/controller/src/positions/supply.rs)

### Summary
The EosNow congestion attack exploited cheap, repeated transactions to prevent the game from resolving state. The analog here: `clean_bad_debt` is permissionless but gated on `total_collateral <= $5` (dust), while `supply` lets *any* third party add to an existing supply position of *any* account — including an insolvent one. An attacker can therefore spend ~$6 to push a bad-debt account's collateral just over the dust cap whenever cleanup is attempted, keeping unbacked debt on the books indefinitely.

### Finding Description
`clean_bad_debt` socializes residual insolvent debt only when `is_socializable_bad_debt` holds: `total_debt > total_collateral` and `total_collateral <= 5 WAD` [1](#0-0) . Meanwhile `process_supply` only restricts third parties from opening *new* asset slots; topping up an asset the account already holds is unrestricted [2](#0-1) . An insolvent account that failed cleanup necessarily still holds a collateral leg (collateral > 0), so an attacker can call `supply(caller, victim_account_id, spoke_id, [(existing_collateral_asset, dust_amount)])` to lift collateral above $5 WAD at will, causing every subsequent permissionless `clean_bad_debt` to revert.

The donated collateral is unrecoverable only in the sense that the insolvent owner cannot withdraw, but the attacker's *cost* is one-time ~$5–6 per block attempt, and each re-top-up after any partial liquidation again re-arms the block. The only alternative is the privileged `force_socialize_bad_debt`, which is owner-gated and therefore unavailable as a permissionless mitigation [3](#0-2) .

### Impact Explanation
While blocked, the unbacked debt is never written down via `apply_bad_debt_to_supply_index` — the supply index is not reduced, so suppliers' claims remain nominally inflated while the actual cash backing is short. Withdrawals against that market hit `InsufficientLiquidity`/backing-shortfall gates, i.e., a persistent (indefinite) freezing of lender funds in the affected market and delayed recognition of protocol insolvency. Because the same dust collateral also inhibits pro-rata seizure rounding, normal liquidators get no incentive path to close the residue either.

### Likelihood Explanation
Requires only: an insolvent account with residual collateral ≤ $5 (the exact post-liquidation dust state the design anticipates), a listed asset the account already supplies, and ~$6 of tokens. The call is a single unprivileged `supply` transaction, fully front-runnable against any observed `clean_bad_debt` attempt — directly mirroring the repeated-transaction congestion pattern in the source incident. Medium likelihood: it needs an ongoing motive to grief a specific market rather than direct profit, though blocking cleanup also shields a colluding borrower's zombie account and can be combined with spamming cleanup reverts.

### Recommendation
Make the dust check robust to donations, e.g.:

- Evaluate the ≤$5 threshold against collateral *excluding* amounts supplied after the account became liquidatable/insolvent, or snapshot collateral at the time insolvency was established, or
- Allow `clean_bad_debt` to first seize/sweep the residual collateral into revenue regardless of its exact value (raise or remove the dust cap for accounts proven insolvent over a sustained period), or
- Restrict third-party `supply` top-ups to solvent accounts (require post-supply state not to worsen the bad-debt eligibility check is insufficient — instead block top-ups on accounts with `HF < 1` entirely, since topping up an insolvent account has no legitimate economic purpose for a non-owner).

### Proof of Concept
1. Borrower opens an account, supplies collateral, borrows; price moves make HF < 1.
2. Liquidators seize collateral down to a small residual; account ends with `total_debt > total_collateral` and `total_collateral = $4` — eligible for `clean_bad_debt`.
3. Attacker calls `controller::supply(attacker, victim_id, spoke_id, [(hub_asset_of_existing_collateral, amount_worth_$2)])`. `require_third_party_existing_supply` passes because the asset is already in `supply_positions`.
4. Every `clean_bad_debt(victim_id)` now reverts since `total_collateral = $6 > 5 WAD`.
5. If partial liquidation or price drift pushes collateral back under $5, attacker repeats step 3 with a few cents. The market's bad debt is never socialized; supplier withdrawals remain impaired indefinitely unless the privileged owner path intervenes.

### Citations

**File:** skills/xoxno-lending/math.md (L415-417)
```markdown
## Bad-debt socialization

Eligibility (`is_socializable_bad_debt`): `total_debt > total_collateral` and `total_collateral ≤ 5 WAD` for permissionless `clean_bad_debt` and the check after `liquidate`; owner-only `force_socialize_bad_debt` drops the collateral cap. `contracts/pool/src/interest.rs::apply_bad_debt_to_supply_index` then lowers only the affected market's supply index ([formulas.md#bad-debt](../../docs/reference/formulas.md#bad-debt)). Example: 2,000,000 USDC of shares at index 1.083 (`total_supply_ray = 2_166_000e27`), bad debt 30,000 USDC:
```

**File:** contracts/controller/src/positions/supply.rs (L78-97)
```rust
fn require_third_party_existing_supply(
    env: &Env,
    account_id: u64,
    resolved_account_id: u64,
    caller: &Address,
    account: &Account,
    aggregated: &AggregatedPayments,
) {
    if account_id != 0
        && !account::is_owner_or_delegate(env, resolved_account_id, caller, &account.owner)
    {
        for (hub_asset, _) in aggregated.iter() {
            assert_with_error!(
                env,
                account.supply_positions.contains_key(hub_asset.clone()),
                GenericError::NotAuthorized
            );
        }
    }
}
```

**File:** scripts/permissionless_entrypoints.txt (L72-73)
```text
controller::clean_bad_debt | caller-auth | INV-AUTH-03, INV-LIQ-04 | Anyone may socialize an insolvent account's residual debt, but only once its remaining collateral is at or below the dust threshold; only the owner-gated force_socialize_bad_debt omits the dust cap.
controller::recapitalize | caller-auth | INV-AUTH-03, INV-ACCT-02, INV-ACCT-03 | Anyone may donate their own funds to cover a market's backing shortfall; only the measured receipt up to the shortfall is applied and the excess is refunded to the payer.
```
