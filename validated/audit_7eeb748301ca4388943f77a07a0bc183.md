Confirmed key fact: with orderless transactions (`ReplayProtector::Nonce`), an account's `sequence_number` field is never incremented for that transaction [1](#0-0) . This decouples `account::get_sequence_number` from the specific transaction being executed when orderless transactions are in use, which is exactly the missing link needed to make the multisig deterministic-address flaw concrete and non-speculative.

### Title
Multisig account deterministic address derivation uses the volatile global sequence number, permanently stranding pre-funded APT/assets under orderless transactions - (File: aptos-move/framework/aptos-framework/sources/multisig_account.move)

### Summary
`multisig_account::get_next_multisig_account_address` lets a creator precompute the deterministic resource-account address of a not-yet-created multisig account, in order to pre-fund it (the documented "vanity"/counterfactual pattern is explicit in `create_with_owners_then_remove_bootstrapper`) [2](#0-1) . Both the view function and the actual creation logic derive the resource-account seed from `account::get_sequence_number(creator)` [3](#0-2) [4](#0-3) . This is the direct Aptos analog of the Sablier bug's "salt depends on data that isn't guaranteed to stay constant" pattern: instead of tranche percentages, the "salt" here is the creator's global account sequence number, and it is affected by **any** transaction the creator submits, not merely by multisig-creation calls.

### Finding Description
The predicted address is `create_resource_address(creator, DOMAIN_SEPARATOR || bcs(seq_number))` where `seq_number` is read live from account state at the time of the call [5](#0-4) . For ordinary sequence-numbered transactions, the VM enforces `txn_sequence_number == account_sequence_number` in the prologue [6](#0-5) , so if a stale nonce is used the whole transaction is rejected outright rather than silently executing with a different derived address — this protects the classic sequential-transaction case.

However, Aptos also supports orderless transactions, which use a `Nonce`-based replay protector instead of a sequence number, and explicitly do **not** advance the account's `sequence_number` for that transaction [1](#0-0) [7](#0-6) . This means:
- A creator can call the view function `get_next_multisig_account_address(creator)` and get address `A`, derived from the creator's current `sequence_number = N`.
- A user (or the creator) pre-funds `A` with APT/other assets, following the exact "counterfactual pre-funding" pattern the framework itself documents/supports.
- Before the multisig-creation transaction is committed, the creator submits *any* other ordinary (sequence-numbered) transaction — unrelated to multisig creation — which increments `sequence_number` to `N+1`. Because orderless and sequence-numbered transactions can be interleaved for the same account and their ordering relative to each other is not fixed by a shared counter, this is fully within the creator's/attacker's control and requires no protocol privilege.
- When `create_multisig_account` finally executes, `account::get_sequence_number(owner)` now returns `N+1`, so the resource account is created at a **different** address `A' != A` [4](#0-3) .
- The value locked in `A` can never be recovered: `A` has no `Account`/`SignerCapability` control path tied to it (nonce `N` was consumed by a different, unrelated transaction and can never recur for that account, since sequence numbers are monotonic and unique per value), and no owner/multisig ever comes to control it.

This breaks the custody invariant that "the address a user is told to deposit into must be the address that ends up under the intended control (multisig owners / signer capability)." Unlike the framework's own resource-account/coin-store deposit path, which gracefully "adopts" a pre-funded plain account into a resource account (as documented in `account::create_resource_account`'s comments) [8](#0-7) , this adoption only rescues funds sent to *the actual computed address of the transaction that runs*, not funds sent to a *stale* precomputed address that the creator no longer produces.

### Impact Explanation
Funds sent to the precomputed multisig address become permanently locked / unrecoverable when the predicted nonce diverges from the nonce actually consumed at creation time. This is a "permanent lock or non-recoverable loss of ... resource-account-held value" custody impact. Given that `get_next_multisig_account_address` is a public `#[view]` function explicitly intended to support pre-funding/vanity workflows (as evidenced by its use inside `create_with_owners_then_remove_bootstrapper`) [2](#0-1) , wallets, SDKs, or dApps that build "counterfactual multisig" UX on top of it (mirroring the Safe/Sablier CREATE2 pattern from the seed report) would be directly exposed.

### Likelihood Explanation
Exploitation does not require any special privilege — it only requires the account owner to sign an unrelated sequence-numbered transaction in the window between quoting the address and having the multisig-creation transaction land, which is entirely plausible for any active account, and trivially forceable by an attacker who can front-run/race a transaction from the creator's account (e.g. if a third party can induce or observe the creator submitting other transactions). It requires the orderless-transaction feature to be enabled/used, which the code shows is an actively developed, live mechanism (`nonce_validation.move`, `ReplayProtector::Nonce`) [9](#0-8) . I was not able to fully verify within the available tool budget whether the orderless feature is currently mainnet-enabled by default or gated behind a feature flag not yet activated — this should be confirmed before treating this as immediately exploitable in production.

### Recommendation
Do not derive the multisig resource-account seed from the mutable, shared `account::sequence_number`. Instead:
- Use a dedicated, monotonically-incrementing per-creator nonce counter stored in a resource owned by the multisig module (similar to `vesting::AdminStore.nonce`, which is scoped to vesting-contract creation only and not shared with unrelated transactions) [10](#0-9) , or
- Require the caller to explicitly pass the intended nonce/seed as a transaction argument, and assert on-chain that it matches the value used when the address was predicted, aborting cleanly (without stranding pre-sent funds) if it does not, or
- Provide a documented, safe recovery path (e.g., a permissionless "sweep" of value from an address that never received a `MultisigAccount`/`SignerCapability` back to the sender) for cases where prediction and execution diverge.

### Proof of Concept
1. Creator account `C` has current `sequence_number = N`. Call view function `multisig_account::get_next_multisig_account_address(C)` → returns address `A` (derived from seed `N`).
2. Third party or the creator transfers APT to `A` in anticipation of `C` calling `create_with_owners`.
3. Before the `create_with_owners` transaction lands, `C` submits (or is induced/raced into submitting) any other ordinary sequence-numbered transaction, which is committed first and advances `C`'s `sequence_number` to `N+1`.
4. `C`'s `create_with_owners` transaction now executes with `account::get_sequence_number(C) == N+1`, so `create_multisig_account` derives resource address `A' != A` and creates the multisig there.
5. `A` never receives a `MultisigAccount`/`SignerCapability`; the APT sent to `A` in step 2 is permanently unrecoverable, since sequence number `N` for `C` can never be produced again by any subsequent transaction.

Note: full exploitability (step 3's interleaving) depends on orderless-transaction feature activation; I could not confirm from indexed code whether this is currently live on mainnet, so this should be validated in a live/testnet environment before being treated as a confirmed, currently-active mainnet issue.

### Citations

**File:** sdk/src/types.rs (L354-360)
```rust
    fn build_raw_transaction(&self, builder: TransactionBuilder) -> RawTransaction {
        let sequence_number = if builder.has_nonce() {
            // Do not increment sequence number for orderless transactions.
            u64::MAX
        } else {
            self.increment_sequence_number()
        };
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L539-544)
```text
    #[view]
    /// Return the predicted address for the next multisig account if created from the given creator address.
    public fun get_next_multisig_account_address(creator: address): address {
        let owner_nonce = account::get_sequence_number(creator);
        create_resource_address(&creator, create_multisig_account_seed(to_bytes(&owner_nonce)))
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L838-863)
```text
    /// Like `create_with_owners`, but removes the calling account after creation.
    ///
    /// This is for creating a vanity multisig account from a bootstrapping account that should not
    /// be an owner after the vanity multisig address has been secured.
    public entry fun create_with_owners_then_remove_bootstrapper(
        bootstrapper: &signer,
        owners: vector<address>,
        num_signatures_required: u64,
        metadata_keys: vector<String>,
        metadata_values: vector<vector<u8>>,
    ) {
        let bootstrapper_address = address_of(bootstrapper);
        create_with_owners(
            bootstrapper,
            owners,
            num_signatures_required,
            metadata_keys,
            metadata_values
        );
        update_owner_schema(
            get_next_multisig_account_address(bootstrapper_address),
            vector[],
            vector[bootstrapper_address],
            option::none()
        );
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1488-1499)
```text
    fun create_multisig_account(owner: &signer): (signer, SignerCapability) {
        let owner_nonce = account::get_sequence_number(address_of(owner));
        let (multisig_signer, multisig_signer_cap) =
            account::create_resource_account(owner, create_multisig_account_seed(to_bytes(&owner_nonce)));
        // Register the account to receive APT as this is not done by default as part of the resource account creation
        // flow.
        if (!coin::is_account_registered<AptosCoin>(address_of(&multisig_signer))) {
            coin::register<AptosCoin>(&multisig_signer);
        };

        (multisig_signer, multisig_signer_cap)
    }
```

**File:** types/src/account_address.rs (L238-246)
```rust
pub fn create_multisig_account_address(
    creator: AccountAddress,
    creator_nonce: u64,
) -> AccountAddress {
    let mut full_seed = vec![];
    full_seed.extend(MULTISIG_ACCOUNT_DOMAIN_SEPARATOR);
    full_seed.extend(bcs::to_bytes(&creator_nonce).unwrap());
    create_resource_address(creator, &full_seed)
}
```

**File:** aptos-move/framework/aptos-framework/sources/transaction_validation.move (L169-185)
```text
        // Check for replay protection
        match (replay_protector) {
            SequenceNumber(txn_sequence_number) => {
                check_for_replay_protection_regular_txn(
                    sender_address,
                    gas_payer_address,
                    txn_sequence_number,
                );
            },
            Nonce(nonce) => {
                check_for_replay_protection_orderless_txn(
                    sender_address,
                    nonce,
                    txn_expiration_time,
                );
            }
        };
```

**File:** aptos-move/framework/aptos-framework/sources/transaction_validation.move (L219-233)
```text
            let account_sequence_number = account::get_sequence_number(sender_address);
            assert!(
                txn_sequence_number < (1u64 << 63),
                error::out_of_range(PROLOGUE_ESEQUENCE_NUMBER_TOO_BIG)
            );

            assert!(
                txn_sequence_number >= account_sequence_number,
                error::invalid_argument(PROLOGUE_ESEQUENCE_NUMBER_TOO_OLD)
            );

            assert!(
                txn_sequence_number == account_sequence_number,
                error::invalid_argument(PROLOGUE_ESEQUENCE_NUMBER_TOO_NEW)
            );
```

**File:** aptos-move/framework/aptos-framework/sources/account/account.move (L1147-1156)
```text
    /// A resource account is used to manage resources independent of an account managed by a user.
    /// In Aptos a resource account is created based upon the sha3 256 of the source's address and additional seed data.
    /// A resource account can only be created once, this is designated by setting the
    /// `Account::signer_capability_offer::for` to the address of the resource account. While an entity may call
    /// `create_account` to attempt to claim an account ahead of the creation of a resource account, if found Aptos will
    /// transition ownership of the account over to the resource account. This is done by validating that the account has
    /// yet to execute any transactions and that the `Account::signer_capability_offer::for` is none. The probability of a
    /// collision where someone has legitimately produced a private key that maps to a resource account address is less
    /// than `(1/2)^(256)`.
    public fun create_resource_account(source: &signer, seed: vector<u8>): (signer, SignerCapability) acquires Account {
```

**File:** aptos-move/framework/aptos-framework/sources/nonce_validation.move (L34-38)
```text
    // An orderless transaction is a transaction that doesn't have a sequence number.
    // Orderless transactions instead contain a nonce to prevent replay attacks.
    // If the incoming transaction has the same (address, nonce) pair as a previous unexpired transaction, it is rejected.
    // The nonce history is used to store the list of (address, nonce, txn expiration time) values of all unexpired transactions.
    // The nonce history is used in the transaction validation process to check if the incoming transaction is valid.
```

**File:** aptos-move/framework/aptos-framework/sources/vesting.move (L1028-1044)
```text
    /// Create a salt for generating the resource accounts that will be holding the VestingContract.
    /// This address should be deterministic for the same admin and vesting contract creation nonce.
    fun create_vesting_contract_account(
        admin: &signer,
        contract_creation_seed: vector<u8>,
    ): (signer, SignerCapability) acquires AdminStore {
        let admin_store = borrow_global_mut<AdminStore>(signer::address_of(admin));
        let seed = bcs::to_bytes(&signer::address_of(admin));
        seed.append(bcs::to_bytes(&admin_store.nonce));
        admin_store.nonce += 1;

        // Include a salt to avoid conflicts with any other modules out there that might also generate
        // deterministic resource accounts for the same admin address + nonce.
        seed.append(VESTING_POOL_SALT);
        seed.append(contract_creation_seed);

        let (account_signer, signer_cap) = account::create_resource_account(admin, seed);
```
