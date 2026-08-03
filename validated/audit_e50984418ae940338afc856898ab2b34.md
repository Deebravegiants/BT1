This confirms the exploit is real and is even codified as expected/passing behavior in the codebase's own test suite.

### Title
Duplicate `AnyPublicKey` entries in `MultiKey` allow a single signer to satisfy a multi-key threshold, breaking N-of-M custody guarantees - (types/src/transaction/authenticator.rs)

### Summary
`MultiKey::new` and `MultiKeyAuthenticator::new`/`to_single_key_authenticators`/`verify` never check that the public keys inside a `MultiKey` are distinct. An attacker (or a user misconfiguring a "multisig" account) can construct a `MultiKey` containing the same `AnyPublicKey` at two or more bitmap indices with `signatures_required = 2` (or higher), and satisfy the threshold by signing each of those duplicated indices with the single private key that corresponds to the repeated public key. `to_single_key_authenticators` and `verify` accept this as valid, so an account whose authentication key is derived from such a `MultiKey` is, in practice, controlled by a single key even though it appears to require N distinct signers.

### Finding Description
`MultiKey::new` only validates `signatures_required > 0`, an upper bound on key count, and that `signatures_required <= public_keys.len()` — it does not deduplicate or reject repeated `AnyPublicKey` entries: [1](#0-0) 

`MultiKeyAuthenticator::new` only guards against duplicate **bitmap indices**, not duplicate **underlying keys** — signing indices 1 and 2 that happen to reference the same public key is accepted: [2](#0-1) 

`to_single_key_authenticators` / `verify` build one `SingleKeyAuthenticator` per bitmap-set index and check only that the *count* of signatures meets `signatures_required`; it never checks that the signatures come from distinct keys: [3](#0-2) 

The Move-side `multi_key.move` module used to compute authentication keys has the exact same gap — no uniqueness check on `single_keys`: [4](#0-3) 

The codebase's own existing unit test proves the exploit works end-to-end: it builds `keys = [any_sender0_pub, any_sender1_pub, any_sender1_pub]` (the secp256k1 key `any_sender1_pub` is duplicated at indices 1 and 2) with `signatures_required = 2`, then signs indices 1 and 2 both with `sender1`'s single signature (`signature1`), producing `mk_auth_12`, wraps it in `AccountAuthenticator::multi_key`, and calls `signed_txn.verify_signature().unwrap()` — which **succeeds**: [5](#0-4) 

This directly demonstrates that with a 3-key/`2`-required `MultiKey` where key #2 is a duplicate of key #1, the holder of only `sender1`'s private key (plus knowledge of `sender0`'s or `sender1`'s public key material, without needing `sender0`'s private key at all) can satisfy the 2-signature threshold alone by re-signing the duplicated index.

### Impact Explanation
Any custody scheme (multisig-controlled resource account, object owner, or code object) that relies on `MultiKey`/`MultiKeyAuthenticator` for its authentication key inherits this weakness. If the party responsible for assembling the `MultiKey` (during account rotation or resource-account/object creation) includes a duplicate public key — whether by attacker manipulation of an unprivileged key-submission flow, misconfiguration, or supply-chain-style key duplication — the resulting "N-of-M" account is actually controlled by fewer distinct parties than intended, down to just one. This breaks the core custody invariant of threshold multisig: an unprivileged single-key holder can gain full authority to move, freeze, upgrade, or otherwise control all assets held by that authentication key, since transaction-signature verification (`SignedTransaction::verify_signature` via `AccountAuthenticator::multi_key`) is the correct-signer gate for those assets.

### Likelihood Explanation
Exploitation requires that a `MultiKey` with duplicate `AnyPublicKey` entries exists and is bound to an account's authentication key. This is not automatically attacker-controlled in every code path — many trusted UIs/wallets may already deduplicate keys before rotation — but there is no protocol-level, VM-level, or Move-level enforcement preventing duplicates anywhere in the stack (`MultiKey::new`, `MultiKeyAuthenticator::new`, `multi_key.move`). Any unprivileged code path that lets a user or attacker supply the list of `AnyPublicKey`s for account creation/rotation (e.g., `rotate_authentication_key`, resource-account creation with a custom multisig scheme, or object ownership set to a `MultiKey`-derived address) is exposed. Given the total absence of validation and the fact that it is validated as "working" by the project's own test suite, this is a systemic gap rather than a hypothetical edge case.

### Recommendation
- Add a uniqueness check on `public_keys` in `MultiKey::new` (Rust) and `new_multi_key_from_single_keys`/`deserialize_multi_key` (Move), rejecting any `MultiKey` containing duplicate `AnyPublicKey` entries, with a dedicated error code.
- Add equivalent validation in `MultiKeyAuthenticator::to_single_key_authenticators`/`verify` (or ideally reject construction of duplicate-containing `MultiKey`s before an authentication key can ever be derived from them), so no on-chain account can be created with a non-distinct key set.
- Add a regression test asserting `MultiKey::new` / `verify_signature` **fails** for duplicate-key inputs (the current test at `verify_multi_key_auth` asserts the opposite and should be corrected to reflect a rejection, not `unwrap()` success).

### Proof of Concept
The existing test in the repository already demonstrates the break; the critical portion is: [6](#0-5) [5](#0-4) 

This shows `MultiKey::new(vec![any_sender0_pub, any_sender1_pub, any_sender1_pub], 2)` succeeding, and a `MultiKeyAuthenticator` signing bitmap indices 1 and 2 — both mapped to the same duplicated `any_sender1_pub` key — with the single `signature1` from `sender1`, and `signed_txn.verify_signature()` returning `Ok(())`. This is precisely the described attack: a single private key (`sender1`) alone satisfies a `signatures_required = 2` threshold, without ever needing `sender0`'s private key.

### Citations

**File:** types/src/transaction/authenticator.rs (L1119-1151)
```rust
impl MultiKeyAuthenticator {
    pub fn new(public_keys: MultiKey, signatures: Vec<(u8, AnySignature)>) -> Result<Self> {
        ensure!(
            public_keys.len() < (u8::MAX as usize),
            "Too many public keys, {}, in MultiKeyAuthenticator.",
            public_keys.len(),
        );

        let mut signatures_bitmap = aptos_bitvec::BitVec::with_num_bits(public_keys.len() as u16);
        let mut any_signatures = vec![];

        for (idx, signature) in signatures {
            ensure!(
                (idx as usize) < public_keys.len(),
                "Signature index is out of public key range, {} < {}.",
                idx,
                public_keys.len(),
            );
            ensure!(
                !signatures_bitmap.is_set(idx as u16),
                "Duplicate signature index, {}.",
                idx
            );
            signatures_bitmap.set(idx as u16);
            any_signatures.push(signature);
        }

        Ok(MultiKeyAuthenticator {
            public_keys,
            signatures: any_signatures,
            signatures_bitmap,
        })
    }
```

**File:** types/src/transaction/authenticator.rs (L1167-1207)
```rust
    pub fn to_single_key_authenticators(&self) -> Result<Vec<SingleKeyAuthenticator>> {
        ensure!(
            self.signatures_bitmap.last_set_bit().is_some(),
            "There were no signatures set in the bitmap."
        );

        ensure!(
            (self.signatures_bitmap.last_set_bit().unwrap() as usize) < self.public_keys.len(),
            "Mismatch in the position of the last signature and the number of PKs, {} >= {}.",
            self.signatures_bitmap.last_set_bit().unwrap(),
            self.public_keys.len(),
        );
        ensure!(
            self.signatures_bitmap.count_ones() as usize == self.signatures.len(),
            "Mismatch in number of signatures and the number of bits set in the signatures_bitmap, {} != {}.",
            self.signatures_bitmap.count_ones(),
            self.signatures.len(),
        );
        ensure!(
            self.signatures.len() >= self.public_keys.signatures_required() as usize,
            "Not enough signatures for verification, {} < {}.",
            self.signatures.len(),
            self.public_keys.signatures_required(),
        );
        let authenticators: Vec<SingleKeyAuthenticator> =
            std::iter::zip(self.signatures_bitmap.iter_ones(), self.signatures.iter())
                .map(|(idx, sig)| SingleKeyAuthenticator {
                    public_key: self.public_keys.public_keys[idx].clone(),
                    signature: sig.clone(),
                })
                .collect();
        Ok(authenticators)
    }

    pub fn verify<T: Serialize + CryptoHash>(&self, message: &T) -> Result<()> {
        let authenticators = self.to_single_key_authenticators()?;
        authenticators
            .iter()
            .try_for_each(|authenticator| authenticator.verify(message))?;
        Ok(())
    }
```

**File:** types/src/transaction/authenticator.rs (L1241-1264)
```rust
    pub fn new(public_keys: Vec<AnyPublicKey>, signatures_required: u8) -> Result<Self> {
        ensure!(
            signatures_required > 0,
            "The number of required signatures is 0."
        );

        ensure!(
            public_keys.len() <= MAX_NUM_OF_SIGS, // This max number of signatures is also the max number of public keys.
            "The number of public keys is greater than {}.",
            MAX_NUM_OF_SIGS
        );

        ensure!(
            public_keys.len() >= signatures_required as usize,
            "The number of public keys is smaller than the number of required signatures, {} < {}",
            public_keys.len(),
            signatures_required
        );

        Ok(Self {
            public_keys,
            signatures_required,
        })
    }
```

**File:** types/src/transaction/authenticator.rs (L1845-1850)
```rust
        let keys = vec![
            any_sender0_pub.clone(),
            any_sender1_pub.clone(),
            any_sender1_pub.clone(),
        ];
        let multi_key = MultiKey::new(keys, 2).unwrap();
```

**File:** types/src/transaction/authenticator.rs (L1920-1932)
```rust
        let mk_auth_12 = MultiKeyAuthenticator::new(multi_key.clone(), vec![
            (1, signature1.clone()),
            (2, signature1.clone()),
        ])
        .unwrap();
        let single_key_authenticators = mk_auth_12.to_single_key_authenticators().unwrap();
        assert_eq!(single_key_authenticators, vec![
            sender1_auth.clone(),
            sender1_auth.clone()
        ]);
        let account_auth = AccountAuthenticator::multi_key(mk_auth_12);
        let signed_txn = SignedTransaction::new_single_sender(raw_txn.clone(), account_auth);
        signed_txn.verify_signature().unwrap();
```

**File:** aptos-move/framework/aptos-stdlib/sources/cryptography/multi_key.move (L58-74)
```text
    /// Creates a new MultiKey public key from a vector of single key public keys and a number representing the number of signatures required to authenticate a transaction.
    public fun new_multi_key_from_single_keys(single_keys: vector<single_key::AnyPublicKey>, signatures_required: u8): MultiKey {
        let num_keys = single_keys.length();
        assert!(
            num_keys > 0,
            error::invalid_argument(E_INVALID_MULTI_KEY_NO_KEYS)
        );
        assert!(
            num_keys <= MAX_NUMBER_OF_PUBLIC_KEYS,
            error::invalid_argument(E_INVALID_MULTI_KEY_TOO_MANY_KEYS)
        );
        assert!(
            (signatures_required as u64) <= num_keys,
            error::invalid_argument(E_INVALID_MULTI_KEY_SIGNATURES_REQUIRED)
        );
        MultiKey { public_keys: single_keys, signatures_required }
    }
```
