## Title
Unscoped `Capability` revocation in `common_account::remove_account` lets an unrelated admin destroy any address's resource-account signer capability - (File: aptos-move/move-examples/common_account/sources/common_account.move)

### Summary
`common_account::common_account` lets a `Management.admin` revoke a delegate's ability to generate the resource-account signer by deleting the delegate's `Capability` resource. However, `remove_account` never verifies that the victim's stored `Capability.common_account` actually matches the `common_account` the caller administers. Because `Capability` is a global, non-parameterized `key` resource (only one can exist per address, for whichever common account the address last claimed), any address that is merely `admin` of *some* common account (including one it just created for free) can destroy the `Capability` of any other address that happens to hold a claim for a *completely unrelated* common account.

### Finding Description
`Capability` is declared as a singleton resource keyed only by the holder's address, with no way to have more than one active claim per user: [1](#0-0) 

`remove_account` is supposed to strip a delegate's access to a *specific* `common_account`. When the delegate is not still in the ACL's `unclaimed_capabilities` map (i.e., it already claimed its `Capability`), the function falls back to asserting only that *some* `Capability` resource exists at `other`'s address, then unconditionally destroys it - without ever checking that this `Capability`'s `common_account` field equals the `common_account` parameter the caller administers: [2](#0-1) 

By contrast, `acquire_signer` *does* perform this exact scoping check before using the capability: [3](#0-2) 

The presence of this check in `acquire_signer` (and a dedicated test `test_wrong_cap` for the "capability belongs to a different common account" case) shows the module's authors were aware of the multi-common-account confusion risk, but the same guard is missing from `remove_account`.

### Impact Explanation
Any account can call `create()` to become the `admin` of its own throwaway common account at zero cost: [4](#0-3) 

That admin can then call `remove_account(attacker, attacker_common_account, victim)` for **any** `victim` address, with no prior relationship to the attacker's common account required. As long as `victim` currently holds a `Capability` for some other, legitimate common account (e.g., one managing a resource account holding LP tokens, coins, or other pooled assets per the resource-account custody pattern documented in `resource_account.move`), that `Capability` is silently deleted. The victim permanently loses the ability to generate the shared resource-account signer via `acquire_signer` for the legitimate account it was actually authorized on, since `acquire_capability`/`acquire_signer` require either an existing `Capability` or a still-pending ACL entry - both of which are now gone. This is an unauthorized revocation of resource-account control that can permanently deny a legitimate holder access to custody-controlling authority over resource-account-held value, satisfying the "unauthorized takeover/loss of resource-account control tied to live assets" impact class.

### Likelihood Explanation
Exploitation requires no special privilege beyond being able to submit a transaction (create an account/common_account) and knowing a target address that has an active `Capability` for some other common account - such claims are public on-chain state. No cooperation from the victim or from the legitimate common account's real admin is needed, making this trivially and repeatedly exploitable as a griefing/DoS primitive against any user of this module.

### Recommendation
In `remove_account`, before destroying the `Capability`, load it and assert that `capability.common_account == common_account` (mirroring the check already performed in `acquire_signer`), and only then `move_from` it. Alternatively, restructure `Capability` to be scoped per `common_account` (e.g., stored in a table under the common account, or parameterized so multiple claims can coexist without cross-account collision).

### Proof of Concept
1. Legitimate flow: Bob (`victim`) is added and claims a `Capability` for `common_account_B` (owned/administered by a legitimate project via `create`/`add_account`/`acquire_capability`), giving Bob the right to call `acquire_signer(bob, common_account_B)`.
2. Attack: Attacker calls `create(attacker, seed)` to create `common_account_A`, becoming its `admin` for free.
3. Attacker calls `remove_account(attacker, common_account_A, bob_addr)`. Since `bob_addr` is not in `common_account_A`'s `unclaimed_capabilities`, the `else` branch runs: it asserts `exists<Capability>(bob_addr)` (true, from step 1) and calls `move_from<Capability>(bob_addr)`, deleting Bob's `Capability` - with no check that this capability belongs to `common_account_A`.
4. Bob can no longer call `acquire_signer(bob, common_account_B)` for the legitimate account he was authorized on, because his `Capability` is gone and he was never re-added to `common_account_B`'s ACL - permanently locking him out of the resource-account signer he legitimately controlled.

### Citations

**File:** aptos-move/move-examples/common_account/sources/common_account.move (L43-46)
```text
    /// A revokable capability that is stored on a users account.
    struct Capability has drop, key {
        common_account: address,
    }
```

**File:** aptos-move/move-examples/common_account/sources/common_account.move (L48-61)
```text
    /// Creates a new common account by creating a resource account and storing the capability.
    public entry fun create(sender: &signer, seed: vector<u8>) {
        let (resource_signer, signer_cap) = account::create_resource_account(sender, seed);

        move_to(
            &resource_signer,
            Management {
                admin: signer::address_of(sender),
                unclaimed_capabilities: simple_map::create(),
            },
        );

        move_to(&resource_signer, CommonAccount { signer_cap });
    }
```

**File:** aptos-move/move-examples/common_account/sources/common_account.move (L74-87)
```text
    /// Remove an account from the management group.
    public entry fun remove_account(
        admin: &signer,
        common_account: address,
        other: address,
    ) acquires Capability, Management {
        let management = assert_is_admin(admin, common_account);
        if (simple_map::contains_key(&management.unclaimed_capabilities, &other)) {
            simple_map::remove(&mut management.unclaimed_capabilities, &other);
        } else {
            assert!(exists<Capability>(other), error::not_found(ENO_CAPABILITY_FOUND));
            move_from<Capability>(other);
        }
    }
```

**File:** aptos-move/move-examples/common_account/sources/common_account.move (L106-124)
```text
    /// Generate a signer for the common_account if permissions allow.
    public fun acquire_signer(
        sender: &signer,
        common_account: address,
    ): signer acquires Capability, CommonAccount, Management {
        let sender_addr = signer::address_of(sender);
        if (!exists<Capability>(sender_addr)) {
          acquire_capability(sender, common_account)
        };
        let capability = borrow_global<Capability>(sender_addr);

        assert!(
            capability.common_account == common_account,
            error::invalid_state(EUNEXPECTED_PARALLEL_ACCOUNT),
        );

        let resource = borrow_global<CommonAccount>(common_account);
        account::create_signer_with_capability(&resource.signer_cap)
    }
```
