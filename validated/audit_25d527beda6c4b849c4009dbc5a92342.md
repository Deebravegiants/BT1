### Title
Frozen or non-allowlisted suppliers can redeem collateral through an arbitrary withdrawal recipient - ([File: contracts/controller/src/positions/supply.rs](contracts/controller/src/positions/supply.rs))

### Summary
`withdraw` authenticates only the position owner or delegate, but permits that caller to choose any external `to` recipient. The pool then performs a token transfer from the pool to that recipient. For externally gated assets such as an RWA token, the token contract validates the sender pool and recipient, but never sees the frozen or removed-from-allowlist account owner. A restricted supplier can therefore redeem its collateral by naming an allowlisted, unfrozen accomplice or second address as the payout recipient.

### Finding Description
In `process_withdraw`, the caller must be authorized and must own or delegate the account, but `to.unwrap_or_else(|| caller.clone())` allows an arbitrary recipient. `require_external_recipient` only rejects protocol-internal recipients; it does not tie the recipient to the account owner or verify any asset-level transfer restriction.

The withdrawal legs are then sent to `pool_withdraw_call` with that recipient. In the pool, `apply` calls `cache.transfer_out(receiver, outcome.net_transfer)`, causing the underlying token transfer to be `pool -> receiver`. An RWA-style gated token that checks only `from` and `to` sees two permitted parties and allows the redemption even though the economic owner is frozen or not allowlisted.

### Impact Explanation
A frozen or non-allowlisted supplier can permanently extract the value of locked collateral by directing the payout to an unrestricted address. This bypasses the token issuer's restriction on the economic redemption and can move funds to an accomplice or newly created address. Because the account owner's collateral shares are burned, this is a direct extraction of user-controlled funds under a restriction intended to prevent that owner from transferring or redeeming the asset.

### Likelihood Explanation
Any unprivileged account owner or delegate can reach the path through `withdraw(account_id, withdrawals, Some(recipient))`. No privileged role, malformed parameter, oracle manipulation, or third-party cooperation is required beyond choosing a recipient address that the gated token accepts. The issue affects any listed collateral whose token enforces allowlist or freeze restrictions on ordinary transfers.

### Recommendation
For restricted assets, do not allow the redemption beneficiary to differ blindly from the account owner. Either:

- require `to == caller` or `to == account.owner` for gated collateral;
- query/enforce the collateral token's transfer restriction against both the economic owner and payout recipient before burning supply shares; or
- introduce an issuer-approved redemption recipient mechanism.

The check must occur before the pool burns supply shares and transfers the underlying asset.

### Proof of Concept
1. A user supplies an RWA-gated collateral token through `supply`, receiving pool supply shares in their lending account.
2. The token issuer later freezes the user or removes the user from the allowlist.
3. The user calls:

   ```text
   withdraw(
       caller = restricted_user,
       account_id = user_account_id,
       withdrawals = [(restricted_collateral, amount_or_zero_for_all)],
       to = Some(allowlisted_accomplice)
   )
   ```

4. The controller authorizes the call because `caller` owns the account.
5. `process_withdraw` accepts `allowlisted_accomplice` as the recipient.
6. The pool burns the user's supply shares and calls the underlying token's `transfer(pool, allowlisted_accomplice, amount)`.
7. The gated token validates `pool` and `allowlisted_accomplice`; both are acceptable, so the transfer succeeds.
8. The restricted user's shares are burned and the accomplice receives the underlying collateral, completing a redemption that a direct `pool -> restricted_user` transfer was intended to block.