### Title
`dissolve` burns unsolicited third-party transfers sent to a crowdloan fund's pot account - (File: polkadot/runtime/common/src/crowdloan/mod.rs)

### Summary
`Pallet::dissolve` is callable by any signed account once a fund's `raised` counter is zero and its retirement period has elapsed. The extrinsic unconditionally sets the pot account's free balance to zero via `CurrencyOf::<T>::make_free_balance_be(&fund_account, Zero::zero())`, regardless of the account's actual balance, rather than checking that the actual balance is already zero or only debiting the amount it expects to be there.

### Finding Description
The crowdloan pot account returned by `Pallet::fund_account_id` is a normal derived `AccountId`, not a keyless/frozen account, so any account can send it a balance transfer via the ordinary `pallet_balances::transfer` extrinsic. This is exactly the scenario exercised by the `withdraw_cannot_be_griefed` test, which proves the pallet must tolerate stray/unsolicited transfers landing on the pot account outside of the crowdloan contribution machinery, i.e., the pot's real free balance can diverge from the internal `fund.raised` accounting variable.

`dissolve` gates on the internal accounting field (`fund.raised.is_zero()`), not on the account's actual on-chain balance. Once all real contributors have been refunded and `fund.raised` reaches zero, any unprivileged signed account can call `dissolve(index)`. The function then reaches `CurrencyOf::<T>::make_free_balance_be(&fund_account, Zero::zero())`, which forcibly overwrites the pot's free balance to zero. If a third party sent an unsolicited transfer to the pot after (or independent of) the refund process — the same class of transfer proven possible by `withdraw_cannot_be_griefed` — that balance is destroyed with no corresponding transfer out and no credit to any account, permanently reducing `Balances::total_issuance()` by that amount.

No signature, origin, or balance check in `dissolve` inspects the pot's real free balance before zeroing it; the only gates are the retirement-period timing check and `fund.raised.is_zero()`, neither of which reflects unsolicited deposits. This is a bad-accounting bug: the pallet conflates "internal contribution ledger is empty" with "the account holds nothing," and the destructive `make_free_balance_be` call assumes the latter without verifying it.

### Impact Explanation
Any unprivileged account can trigger permanent, irreversible burning of tokens belonging to an unrelated third party who merely sent a transfer to a crowdloan's pot account (accidentally or otherwise), as long as the fund has reached the dissolvable state. This violates the invariant that user-controlled assets must remain fully backed and that no unprivileged user should be able to burn assets they do not control. The impact is scoped and concrete: total issuance decreases by exactly the stray amount, and the depositor of that stray amount has no path to recovery once `dissolve` executes.

### Likelihood Explanation
Preconditions are easily attacker-achievable: wait for (or be) the fund whose contributions have all been refunded (`fund.raised == 0`) and whose retirement period has passed — both are normal end-of-life states for any crowdloan. An attacker (or even an innocent user) sends a transfer to the well-known, deterministically-derived pot account (`fund_account_id(index)`), then any signed account calls `dissolve(index)`. This requires no governance, no proxy/multisig trickery, and no special privilege — a plain signed extrinsic. It is fully repeatable across any dissolvable fund.

### Recommendation
Before zeroing the pot balance in `dissolve`, read the account's actual free balance and only clear the amount that is unaccounted for by returning/burning it deliberately (e.g., route any residual balance to the depositor, to a treasury, or explicitly document/burn it as a conscious governance decision) instead of relying on `fund.raised` as a proxy for the account's real balance. Alternatively, if intentionally sweeping dust is the desired design, this should be explicitly documented as accepted behavior and any residual balance should be transferred to the fund depositor rather than silently destroyed via `make_free_balance_be`.

### Proof of Concept
Rust integration test (extension of the existing `withdraw_cannot_be_griefed` pattern) in `polkadot/runtime/common/src/crowdloan/mod.rs` tests module:
1. Create a fund, contribute, let it end without winning, refund all contributions so `fund.raised == 0`.
2. From an unrelated account `griefer`, call `Balances::transfer_allow_death(griefer_origin, fund_account_id(index), stray_amount)` directly to the pot account.
3. Record `Balances::total_issuance()` and the pot account's free balance (`stray_amount` confirmed present).
4. Advance blocks past the retirement period.
5. From any unprivileged signed account (not the depositor), call `Crowdloan::dissolve(origin, index)`.
6. Assert:
   - `Balances::total_issuance()` after == `total_issuance` before minus `stray_amount`.
   - Pot account free balance == 0.
   - The call succeeded (`Ok(())`) with a plain signed origin, proving no privilege was required.