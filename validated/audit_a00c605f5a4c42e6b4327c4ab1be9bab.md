## Analysis

**Reduced custody invariant from the external bug:** when a privileged delegate/authority is changed or revoked, *all* previously granted authority/approval tied to the old delegate must be revoked atomically — otherwise a stale grant survives the "revocation" and can still be exercised.

**Candidate paths considered:**
1. `multisig_account.move` `swap_owner`/`remove_owners` — all owner changes route through `update_owner_schema`, which validates signature-count invariants atomically; no stale-authority path found.
2. `dispatchable_fungible_asset.move` register/withdraw/deposit hooks — dispatch function references are stored per-metadata object and are set once at object creation (`register_dispatch_functions`), not "swappable" afterward, so no analogous re-approval gap.
3. `account.move` rotation/signer capability offers — `offer_rotation_capability` explicitly *overwrites* (`swap_or_fill`) the existing offer, so changing the delegate correctly revokes the old one.
4. **`nft_dao.move` `disable_admin` vs. `pending_admin` offer/claim flow** — this is the strongest analog: an admin-change mechanism (`offer_admin`/`claim_admin`) that leaves a stale delegated grant (`pending_admin`) unrevoked when authority is supposed to be permanently removed via `disable_admin`.

This last one independently holds with an exact code path, so I report it.

### Title
Stale `pending_admin` offer is not cleared by `disable_admin`, allowing a previously-offered address to resurrect full DAO admin authority - (File: `aptos-move/move-examples/dao/nft_dao/sources/nft_dao.move`)

### Summary
`DAO.pending_admin` is set by `offer_admin` and is only ever cleared by `cancel_admin_offer` or `claim_admin`. `disable_admin`, whose stated purpose is to permanently strip admin power ("This can be set to 0x0 to remove all admin powers"), does not clear `pending_admin`. If an admin previously offered admin rights to an address and then calls `disable_admin` (e.g., to lock the DAO down after detecting the offer was made in error, by a compromised key, or as part of decentralizing the DAO), the old offer is left intact. The previously-offered address can subsequently call `claim_admin` and become the DAO's admin again, exactly as in the AaveStrategy bug where changing the swapper left the old swapper's approval intact and no new approval was granted for the new one — here, changing/removing the admin authority leaves an old grant intact that lets an unintended party regain authority.

### Finding Description [1](#0-0) 

`offer_admin` requires the current admin to fill `pending_admin` with `new_admin`, and `cancel_admin_offer` is the only function meant to retract it before it's claimed. [2](#0-1) 

`claim_admin` reads and clears `pending_admin`, then sets `dao_config.admin = new_admin`, permitting the claimant (or the current admin, if `new_admin == @0x0`) to finalize the transfer. [3](#0-2) 

`disable_admin` only sets `dao_config.admin = @0x0` — it never touches `dao_config.pending_admin`. If `pending_admin` currently holds `Some(X)` from a prior unclaimed/uncancelled `offer_admin` call, that offer survives `disable_admin` untouched.

The `DAO` struct fields confirm the two are independent, unlinked pieces of state: [4](#0-3) 

Because `claim_admin`'s only guard is `option::is_some(&dao_config.pending_admin)` plus a caller-address check, address `X` can call `claim_admin` at any time after `disable_admin`, restoring `dao_config.admin` to `X` — directly contradicting the documented "permanently remove all admin powers" semantics of `disable_admin`.

### Impact Explanation
Regaining `dao_config.admin` is custody-grade because DAO admin authority gates:
- `destroy_dao_and_reclaim_signer_capability`, which extracts and returns the DAO's `SignerCapability` (the resource account's signing authority) to whoever holds `admin` at call time — full custody takeover of the resource account and everything it holds: [5](#0-4) 
- `admin_resolve` / `admin_veto_proposal`, letting the resurrected admin override on-chain governance outcomes, including proposals that move APT or NFTs out of the DAO's resource account.
- `admin_update_dao` / individual `admin_change_dao_*` functions, letting the resurrected admin rewrite voting thresholds, durations, and required voting power to manipulate future proposal outcomes.

An address the current admin explicitly tried to lock out (via `disable_admin`) can silently regain full admin control and, from there, unilaterally reclaim the `SignerCapability` backing the DAO's resource account — a non-recoverable, unprivileged owner reassignment of custody-relevant authority.

### Likelihood Explanation
The precondition is narrow but realistic: an admin must have called `offer_admin` and not yet had it claimed or cancelled before calling `disable_admin`. This is plausible in incident-response scenarios (an admin realizes an offered successor is compromised or malicious and tries to lock the DAO by disabling admin entirely, believing this revokes all pending authority) or in routine admin hand-off sequences interrupted by a security concern. No special privilege is needed by the attacker beyond having been the target of a prior (possibly stale or mistaken) `offer_admin` call — no signature forgery, no race condition beyond ordinary transaction ordering.

### Recommendation
Have `disable_admin` also clear any outstanding offer, mirroring how a swapper change must revoke old approvals:
```move
public entry fun disable_admin(admin: &signer, dao: address) acquires DAO {
    assert!(exists<DAO>(dao), error::not_found(EDAO_NOT_EXIST));
    let admin_addr = signer::address_of(admin);
    let dao_config = borrow_global_mut<DAO>(dao);
    assert!(admin_addr == dao_config.admin, error::permission_denied(EINVALID_ADMIN_ACCOUNT));

    // make sure no one can be admin of the DAO
    dao_config.admin = @0x0;
    // revoke any outstanding admin offer so it cannot be claimed later
    if (option::is_some(&dao_config.pending_admin)) {
        option::extract(&mut dao_config.pending_admin);
    };
}
```

### Proof of Concept
1. Admin `A` calls `offer_admin(A, dao, X)` → `dao_config.pending_admin = Some(X)`.
2. Before `X` claims, `A` calls `disable_admin(A, dao)` → `dao_config.admin = @0x0`, but `dao_config.pending_admin` remains `Some(X)`.
3. `X` calls `claim_admin(X, dao)`:
   - `pending_admin` is `Some(X)`, extracted as `new_admin = X`.
   - `new_admin != @0x0`, so the check is `new_admin == caller_address` → `X == X`, passes.
   - `dao_config.admin = X`.
4. `X` is now the DAO admin despite `A`'s attempt to permanently disable admin control, and can call `destroy_dao_and_reclaim_signer_capability(X, dao)` to seize the DAO's `SignerCapability`.

### Citations

**File:** aptos-move/move-examples/dao/nft_dao/sources/nft_dao.move (L132-139)
```text
        /// The signer capability for the resource account where the DAO is hosted (aka the DAO account).
        dao_signer_capability: SignerCapability,
        /// The address of the DAO's admin who has certain permissions over the DAO.
        /// This can be set to 0x0 to remove all admin powers.
        admin: address,
        /// The pending claims waiting for new admin to claim
        pending_admin: Option<address>,
    }
```

**File:** aptos-move/move-examples/dao/nft_dao/sources/nft_dao.move (L513-535)
```text
    /// Offer admin of a DAO to an new admin. The new admin can then claim the offer to be the new admin of the DAO.
    public entry fun offer_admin(admin: &signer, dao: address, new_admin: address) acquires DAO {
        assert!(exists<DAO>(dao), error::not_found(EDAO_NOT_EXIST));
        let admin_addr = signer::address_of(admin);
        let dao_config = borrow_global_mut<DAO>(dao);
        assert!(admin_addr == dao_config.admin, error::permission_denied(EINVALID_ADMIN_ACCOUNT));

        assert!(option::is_none(&dao_config.pending_admin), error::invalid_argument(EADMIN_ALREADY_OFFERED));
        option::fill(&mut dao_config.pending_admin, new_admin);
        nft_dao_events::emit_admin_offer_event(admin_addr, new_admin, dao);
    }

    /// Cancel the admin offer
    public entry fun cancel_admin_offer(admin: &signer, dao: address) acquires DAO {
        assert!(exists<DAO>(dao), error::not_found(EDAO_NOT_EXIST));
        let admin_addr = signer::address_of(admin);
        let dao_config = borrow_global_mut<DAO>(dao);
        assert!(admin_addr == dao_config.admin, error::permission_denied(EINVALID_ADMIN_ACCOUNT));
        // DAO offer exists
        assert!(option::is_some(&dao_config.pending_admin), error::invalid_argument(EADMIN_OFFER_NOT_EXIST));
        option::extract(&mut dao_config.pending_admin);
        nft_dao_events::emit_admin_offer_cancel_event(admin_addr, dao);
    }
```

**File:** aptos-move/move-examples/dao/nft_dao/sources/nft_dao.move (L537-560)
```text
    /// Claim DAO's admin from an offer. The new_admin will become the admin of the DAO.
    public entry fun claim_admin(account: &signer, dao: address) acquires DAO {
        // DAO offer exists
        assert!(exists<DAO>(dao), error::not_found(EDAO_NOT_EXIST));
        let dao_config = borrow_global_mut<DAO>(dao);
        assert!(option::is_some(&dao_config.pending_admin), error::invalid_argument(EADMIN_OFFER_NOT_EXIST));

        // Allow setting the admin to 0x0.
        let new_admin = option::extract(&mut dao_config.pending_admin);
        let old_admin = dao_config.admin;
        let caller_address = signer::address_of(account);
        if (new_admin == @0x0) {
            // If the admin is being updated to 0x0, for security reasons, this finalization must only be done by the
            // current admin.
            assert!(old_admin == caller_address, error::permission_denied(EINVALID_ADMIN_ACCOUNT));
        } else {
            // Otherwise, only the new admin can finalize the transfer.
            assert!(new_admin == caller_address, error::not_found(EADMIN_OFFER_NOT_EXIST));
        };

        // update the DAO's admin address
        dao_config.admin = new_admin;
        nft_dao_events::emit_admin_claim_event(old_admin, new_admin, dao);
    }
```

**File:** aptos-move/move-examples/dao/nft_dao/sources/nft_dao.move (L562-571)
```text
    /// Admin disable the DAO admin through setting the admin to 0x0
    public entry fun disable_admin(admin: &signer, dao: address) acquires DAO {
        assert!(exists<DAO>(dao), error::not_found(EDAO_NOT_EXIST));
        let admin_addr = signer::address_of(admin);
        let dao_config = borrow_global_mut<DAO>(dao);
        assert!(admin_addr == dao_config.admin, error::permission_denied(EINVALID_ADMIN_ACCOUNT));

        // make sure no one can be admin of the DAO
        dao_config.admin = @0x0;
    }
```

**File:** aptos-move/move-examples/dao/nft_dao/sources/nft_dao.move (L640-658)
```text
    /// DAO creator can quit the platform and claim back his resource account signer capability
    public fun destroy_dao_and_reclaim_signer_capability(account: &signer, dao: address): SignerCapability acquires DAO {
        let addr = signer::address_of(account);
        assert!(exists<DAO>(dao), error::not_found(EDAO_NOT_EXIST));
        let dao_config = borrow_global_mut<DAO>(dao);
        assert!(dao_config.admin == addr, error::permission_denied(EINVALID_ADMIN_ACCOUNT));
        let DAO {
            name: _,
            resolve_threshold: _,
            governance_token: _,
            voting_duration: _,
            min_required_proposer_voting_power: _,
            next_proposal_id: _,
            dao_signer_capability,
            admin: _,
            pending_admin: _
        } = move_from<DAO>(dao);
       dao_signer_capability
    }
```
