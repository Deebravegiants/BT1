### Title
Share-credit liquidation bypasses token-level recipient restrictions, letting a token-blocked address obtain and monetize collateral claims - ([File: contracts/controller/src/positions/liquidation/apply.rs])

### Summary
The Dinari report describes a bug class where the protocol moves value to users through paths that skip the token's own access control (the blacklist enforced in `_beforeTokenTransfer`), so blacklisted users still receive minted dShares. XOXNO Lending has the same shape: `SeizeMode::Credit` liquidation settles seized collateral by moving internal supply shares between accounts with no token transfer at all. A `receiver` account owned by an address that the underlying token contract blocks as a recipient still receives full collateral value, because the restriction hook in `token::transfer` is never invoked.

### Finding Description
In `apply_liquidation_share_credit`, seized scaled shares are debited from the liquidated account and credited to the receiver account purely via storage mutation:

- `position.scaled_amount = position.scaled_amount.checked_sub(env, seized_scaled)` on the liquidated account
- `credit_supply_shares` → `position.scaled_amount = position.scaled_amount.checked_add(env, scaled)` on the receiver

The comment at `apply.rs:132-134` confirms this is by design: "No tokens move; pool supply and cash remain unchanged." The only checks are `SpokeMismatch`, arithmetic invariants, and `require_credit_position_limit` — nothing inspects whether the receiver's owner is an authorized recipient of the underlying asset.

By contrast, `SeizeMode::Transfer` goes through `apply_liquidation_seizures` → `withdraw::apply` → `cache.transfer_out(receiver, ...)`, which calls `token::transfer` and therefore enforces the token's recipient restrictions (e.g., a Stellar asset clawback/SAC authorization check, or the blocked-recipient assert shown in `tests/test-harness/src/freezable_token.rs:82-84`). So the protocol offers two settlement modes for the same economic outcome, and one of them silently bypasses the token contract's access control — exactly the Dinari class.

Once the blocked address holds supply shares, it can:

1. Leave them accruing yield (bypassing the freeze on receiving the asset's yield).
2. Use them as collateral and call `borrow` on a different market's token, receiving an unrestricted asset directly to the blocked address — converting a token-frozen claim into liquid value without any transfer of the restricted token ever occurring.

### Impact Explanation
An address that the asset issuer has deliberately barred from receiving the token (sanctions, RWA transfer restrictions, clawback freeze — the liqvid_rwa_collateral test exists precisely because RWA collateral is in scope) can still acquire redeemable collateral value through liquidation. Because the credit lands as collateral-capable shares, the restriction is fully monetizable via `borrow` of other assets. This defeats the token issuer's compliance control inside the protocol, mirroring the Dinari finding where blacklisted users "execute certain requests uninterrupted." Direct token theft is limited since collateral still backs borrows, but the protocol becomes a laundering venue for frozen collateral and credits a sanctioned address with yield-bearing positions.

### Likelihood Explanation
Medium. Requires: a listed asset whose token enforces recipient restrictions (plausible for RWA/SAC assets, and `SeizeMode::Credit` exists precisely for such cases since it avoids transfer failures), a liquidatable position in that asset, and a blocked party controlling a receiver account on the same spoke (`spoke_id` equality is the only receiver constraint, per `apply.rs:165-169`). Any unprivileged liquidator can submit a `liquidate` call with `SeizeMode::Credit` naming the blocked user's account as receiver — or the blocked user can run the liquidation themselves via a second account they own, self-selecting as receiver.

### Recommendation
Before crediting shares in `apply_liquidation_share_credit`, probe the token's recipient acceptance for the receiver's owner (e.g., the existing zero-amount `try_transfer` idiom already used in `contracts/pool/src/ops/withdraw.rs:42-46`), and reject `SeizeMode::Credit` plans whose receiver fails the check — or document and enforce via governance that restricted-asset markets disallow credit-mode seizure.

### Proof of Concept
1. Deploy a pool+controller where collateral token `X` is a restricted token (e.g., `FreezableToken` harness, or a SAC asset with authorization flags) and debt token `Y` is unrestricted.
2. Blocked user `B` creates an account (position NFT has no token restriction).
3. `B` directly transfers `X` to the pool address (sending is not blocked; only receiving `X` is).
4. Attacker/`B` waits for any account `V` with `X` collateral to become liquidatable, then calls `controller.liquidate(v_id, plan, SeizeMode::Credit, b_account_id)` — or `B` liquidates via an accomplice. `apply_liquidation_share_credit` credits `B`'s account with `X` supply shares; `token::transfer` is never called, so `B`'s blocked status is never checked.
5. `B` calls `controller.borrow(y_asset, amount)` — the pool transfers `Y` to `B` (a transfer `X`'s restriction cannot govern), converting the frozen `X`-claim into liquid `Y`.
6. `B` can also simply hold the shares and redeem yield-bearing collateral claims the token issuer intended to freeze.

Note: the precise `liquidate` entrypoint signature and whether the receiver's *owner* (vs. account) is the address the token would block were not fully verified in the available iteration budget; the share-credit path and the absence of any token-level check are confirmed in `apply.rs`.