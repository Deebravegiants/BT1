### Title
`disable_admin` fails to clear `pending_admin`, letting a previously-offered address resurrect DAO admin and drain treasury/NFTs via `admin_resolve` - (File: `aptos-move/move-examples/dao/nft_dao/sources/nft_dao.move`)

### Summary
This is the same custody invariant as the Sublime finding: a privileged "revoke/reset" action leaves a stale pending-approval field set, letting the previously-approved party re-establish privileged control without fresh authorization. In the Aptos NFT DAO example module, `disable_admin` resets `DAO.admin` to `@0x0` but never clears `DAO.pending_admin`, so a stale `offer_admin` offer survives a "disable admin" action and can later be claimed to regain admin authority, which controls direct execution of treasury/NFT-moving proposals via `admin_resolve`.

### Finding Description
`offer_admin` sets `dao_config.pending_admin = Some(new_admin)` [1](#0-0) . The admin can later call `disable_admin`, intended to permanently remove admin authority by setting `dao_config.admin = @0x0`, but this function never touches `pending_admin`: [2](#0-1) 

If the admin had previously issued an `offer_admin` to some address (e.g., intended successor who is later distrusted, or a stale/leaked offer) and then calls `disable_admin` to shut down admin control, the `pending_admin` option is still `Some(new_admin)`. That address can subsequently call `claim_admin`, which only checks that `pending_admin` is set and that the caller matches it — it does not check that `admin` is still non-zero or that the offer is still "live" relative to the disable action: [3](#0-2) 

This resurrects `dao_config.admin` to the stale offeree, defeating the intent of `disable_admin`. Compare with `cancel_admin_offer`, which is the *only* other place `pending_admin` is cleared before claim — exactly mirroring the Sublime bug where `pendingLinkAddresses` was only cleared in `cancelAddressLinkingRequest`, not in the unlink path.

The regained admin role is custody-relevant: `admin_resolve` lets the admin execute a pending proposal immediately, bypassing the normal vote/threshold/time checks used by `resolve`: [4](#0-3) [5](#0-4) 
and `execute_proposal` uses the DAO's resource-account `SignerCapability` to directly transfer APT (`transfer_fund`) or offer NFTs (`offer_nft`) out of the DAO resource account: [6](#0-5) 

### Impact Explanation
Regaining admin control lets an unprivileged (previously offered, now supposed to be revoked) address force-resolve any pending proposal via `admin_resolve`, immediately executing `transfer_fund` (moves `AptosCoin` out of the DAO's resource account) or `offer_nft` (moves NFTs out of the DAO's token store) using the DAO's `SignerCapability` — with no vote-count or time-window requirement. This is a direct custody break: treasury funds and NFTs held by the DAO's resource account can be redirected to attacker-controlled destinations, and the attacker can also veto/resolve governance outcomes (`admin_veto_proposal`) and change DAO parameters (`admin_update_dao`), corrupting the DAO's ownership/control model.

### Likelihood Explanation
This requires that the DAO admin previously issued (and did not cancel) an `offer_admin` to some address, then relied on `disable_admin` to permanently disable admin control (documented usage: "make sure no one can be admin of the DAO"). Since `disable_admin` doesn't warn about or clear outstanding offers, an admin following the documented "disable admin" workflow without separately calling `cancel_admin_offer` is directly exposed. This is plausible operational sequencing (e.g., admin transitions from one admin candidate to "no admin" without realizing a stale offer remains), matching the same operational mistake highlighted in the original Sublime report (calling unlink without calling cancel).

### Recommendation
In `disable_admin`, also clear any outstanding offer:
```move
if (option::is_some(&dao_config.pending_admin)) {
    option::extract(&mut dao_config.pending_admin);
};
dao_config.admin = @0x0;
```
More generally, any function that finalizes/revokes a role (disable, rotate, or reset admin) should also purge any pending offer tied to that role so stale approvals cannot be redeemed afterward.

### Proof of Concept
1. DAO admin `A` calls `offer_admin(A, dao, B)` → `dao_config.pending_admin = Some(B)`.
2. `A` decides `B` should not become admin and, believing this fully revokes admin authority, calls `disable_admin(A, dao)` → `dao_config.admin = @0x0`, but `pending_admin` remains `Some(B)`.
3. `B` calls `claim_admin(B, dao)`. Since `pending_admin = Some(B)` and `new_admin (B) == caller_address (B)`, the check at line 554 passes, and `dao_config.admin` is set to `B` at line 558 — `B` is now the DAO admin despite `A`'s attempt to disable admin entirely.
4. `B` (now admin) creates/controls a proposal and calls `admin_resolve` to immediately execute `transfer_fund`/`offer_nft`, draining the DAO resource account's APT/NFTs, referencing `execute_proposal` at lines 684-705.

Note: this module lives under `aptos-move/move-examples/dao/nft_dao/`, an example/reference DAO implementation rather than aptos-framework core; if any real deployments instantiate this exact module unmodified, the impact applies directly to their treasury custody.

### Citations

**File:** aptos-move/move-examples/dao/nft_dao/sources/nft_dao.move (L494-511)
```text
    /// DAO admin can directly resolve a proposal
    public entry fun admin_resolve(admin: &signer, proposal_id: u64, nft_dao: address, reason: String) acquires DAO, Proposals, ProposalVotingStatistics {
        let resolver = signer::address_of(admin);
        // assert the proposal voting ended
        let proposals = borrow_global<Proposals>(nft_dao);
        assert!(table::contains(&proposals.proposals, proposal_id), error::not_found(EPROPOSAL_NOT_FOUND));
        let proposal = table::borrow(&proposals.proposals, proposal_id);
        // assert the proposal is unresolved yet
        assert!(proposal.resolution == PROPOSAL_PENDING, error::invalid_argument(EPROPOSAL_RESOLVED));
        resolve_internal(option::some(resolver), proposal_id, nft_dao);

        nft_dao_events::emit_admin_resolve_event(
            proposal_id,
            signer::address_of(admin),
            nft_dao,
            reason,
        )
    }
```

**File:** aptos-move/move-examples/dao/nft_dao/sources/nft_dao.move (L514-523)
```text
    public entry fun offer_admin(admin: &signer, dao: address, new_admin: address) acquires DAO {
        assert!(exists<DAO>(dao), error::not_found(EDAO_NOT_EXIST));
        let admin_addr = signer::address_of(admin);
        let dao_config = borrow_global_mut<DAO>(dao);
        assert!(admin_addr == dao_config.admin, error::permission_denied(EINVALID_ADMIN_ACCOUNT));

        assert!(option::is_none(&dao_config.pending_admin), error::invalid_argument(EADMIN_ALREADY_OFFERED));
        option::fill(&mut dao_config.pending_admin, new_admin);
        nft_dao_events::emit_admin_offer_event(admin_addr, new_admin, dao);
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

**File:** aptos-move/move-examples/dao/nft_dao/sources/nft_dao.move (L672-705)
```text
    /////////////////////////// Private functions //////////////////////////////////
    /// Transfer coin from the DAO account to the destination account
    fun transfer_fund(res_acct: &signer, dst: address, amount: u64) {
        coin::transfer<AptosCoin>(res_acct, dst, amount);
    }

    /// offer one NFT from DAO to the DST address. The DST address should
    fun offer_nft(res_acct: &signer, creator: address, collection: String, token_name: String, property_version: u64, dst: address){
        let token_id = create_token_id_raw(creator, collection, token_name, property_version);
        token_transfers::offer(res_acct, dst, token_id, 1);
    }

    /// Internal function for executing a DAO's proposal
    fun execute_proposal(proposal: &Proposal, dao: &DAO){
        vector::enumerate_ref(&proposal.function_names, |i, function_name| {
            let args = vector::borrow(&proposal.function_args, i);
            if (function_name == &string::utf8(b"transfer_fund")) {
                let res_signer = create_signer_with_capability(&dao.dao_signer_capability);
                let dst_addr = property_map::read_address(args, &string::utf8(b"dst"));
                let amount = property_map::read_u64(args, &string::utf8(b"amount"));
                transfer_fund(&res_signer, dst_addr, amount);
            } else if (function_name == &string::utf8(b"offer_nft")) {
                let res_signer = create_signer_with_capability(&dao.dao_signer_capability);
                let creator = property_map::read_address(args, &string::utf8(b"creator"));
                let collection = property_map::read_string(args, &string::utf8(b"collection"));
                let token_name = property_map::read_string(args, &string::utf8(b"token_name"));
                let property_version = property_map::read_u64(args, &string::utf8(b"property_version"));
                let dst = property_map::read_address(args, &string::utf8(b"dst"));
                offer_nft(&res_signer, creator, collection, token_name, property_version, dst);
            } else {
                assert!(function_name == &string::utf8(b"no_op"), error::invalid_argument(ENOT_SUPPROTED_FUNCTION));
            };
        });
    }
```

**File:** aptos-move/move-examples/dao/nft_dao/sources/nft_dao.move (L707-722)
```text
    /// Resolve an proposal
    fun resolve_internal(resolver: Option<address>, proposal_id: u64, nft_dao: address) acquires DAO, Proposals, ProposalVotingStatistics {
        // validate if proposal is ready to resolve
        let dao = borrow_global_mut<DAO>(nft_dao);
        // assert the proposal voting ended
        let proposals = borrow_global_mut<Proposals>(nft_dao);
        let proposal = table::borrow_mut(&mut proposals.proposals, proposal_id);

        if (option::is_some(&resolver)) {
            // only DAO admin can execute the proposal directly
            assert!(*option::borrow(&resolver) == dao.admin, error::permission_denied(EINVALID_ADMIN_ACCOUNT));
            execute_proposal(proposal, dao);
            proposal.resolution = PROPOSAL_RESOLVED_BY_ADMIN;
            // return early befor emitting the normal resolve event.
            return
        };
```
