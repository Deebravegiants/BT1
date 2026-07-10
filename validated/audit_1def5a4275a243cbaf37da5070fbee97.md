### Title
Unimplemented `frost_core::Ciphersuite` Hash Methods in `BLS12381SHA256` Cause Node Panic During CKD Key Generation — (`File: crates/threshold-signatures/src/confidential_key_derivation/ciphersuite.rs`)

---

### Summary

`BLS12381SHA256` implements `frost_core::Ciphersuite` but leaves six required interface methods — `H1`, `H2`, `H3`, `H4`, `H5`, and `HID` — as `unimplemented!()` stubs. If any of these are invoked during the CKD key-generation protocol (particularly `HID`, which the FROST DKG specification uses for identifier derivation), every participating node panics unconditionally. Because the panic occurs inside the distributed computation, no CKD domain key can ever be established, permanently freezing all `request_app_private_key` requests that depend on that domain.

---

### Finding Description

`BLS12381SHA256` is the ciphersuite used for the Confidential Key Derivation (CKD / BLS12-381) domain. It satisfies the `frost_core::Ciphersuite` bound required by `threshold_signatures::keygen`, which is called on every node during CKD key generation:

```
// crates/node/src/providers/ckd/key_generation.rs  line 41-47
let protocol = threshold_signatures::keygen::<BLS12381SHA256, _, _>(
    &cs_participants,
    me.into(),
    self.threshold,
    OsRng,
)?;
run_protocol("CKD key generation", channel, protocol).await
```

The ciphersuite implementation, however, provides only `HDKG` as a real body. The remaining six methods required by the trait are stubs:

```rust
// crates/threshold-signatures/src/confidential_key_derivation/ciphersuite.rs
// comment: "We are currently not using all the functionality.
//           Therefore, I implemented only those that we use."

fn H1(m: &[u8]) -> … { unimplemented!() }   // line 55
fn H2(m: &[u8]) -> … { unimplemented!() }   // line 61
fn H3(m: &[u8]) -> … { unimplemented!() }   // line 65
fn H4(m: &[u8]) -> … { unimplemented!() }   // line 71
fn H5(_m: &[u8]) -> … { unimplemented!() }  // line 75
fn HID(m: &[u8]) -> … { unimplemented!() }  // line 88
```

`HID` is the most critical: the FROST DKG specification uses it for participant-identifier derivation. If `frost_core`'s `keygen` implementation calls `HID` at any point during the DKG rounds, every node executing `run_key_generation_client_internal` panics with a Rust `unimplemented!()` abort. Because the leader and all followers call the same `keygen::<BLS12381SHA256, _, _>()` path (routed through `keygen_computation_inner` → `CKDProvider::run_key_generation_client`), the panic is network-wide and repeatable on every attempt.

The same risk applies to key resharing via `CKDProvider::run_key_resharing_client_internal`.

This is structurally identical to HAL-27: an interface (`frost_core::Ciphersuite`) declares methods that the concrete type (`BLS12381SHA256`) does not actually implement, so any call through the interface fails unconditionally.

---

### Impact Explanation

**Medium — request-lifecycle and participant-state invariant broken.**

If `HID` (or any other stub) is invoked during DKG:

- Every node panics during CKD key generation; the `vote_pk` transaction is never sent.
- The contract's CKD domain remains permanently in the `Initializing` state.
- All subsequent `request_app_private_key` calls for that domain time out and are never fulfilled.
- Key resharing for the CKD domain is equally broken.

No funds are directly stolen, but the CKD service is permanently frozen for the affected domain, breaking the production safety invariant that a successfully initialised domain can serve signing requests.

---

### Likelihood Explanation

**Low-to-Medium.** CKD key generation is triggered whenever the contract enters the `Initializing` state for a BLS12-381 domain. Whether `HID` is actually dispatched by `frost_core`'s DKG implementation depends on the library version; if participants are addressed by raw `u32` indices (as they are here — `Participant::from(participant_id.0)`), `HID` may not be reached. However, the stub is present in production code with no compile-time or runtime guard, and any future upgrade to `frost_core` that exercises `HID` would silently introduce the panic. The risk is non-zero and grows with library evolution.

---

### Recommendation

1. **Implement all six methods** in `BLS12381SHA256` according to the FROST/BLS12-381 specification, or add a compile-time assertion that the `frost_core` version in use never calls the unimplemented methods.
2. **Add a `#[cfg(not(test))] compile_error!`** or a runtime integration test that exercises a full CKD DKG round end-to-end to catch any future `unimplemented!()` panic before deployment.
3. Ensure `BLS12381SHA256` is audited against the full `frost_core::Ciphersuite` contract, not just the subset currently exercised by the CKD protocol.

---

### Proof of Concept

1. Deploy the MPC network with a BLS12-381 CKD domain configured.
2. Observe the contract enter `Initializing` state for that domain.
3. Each node calls `keygen_computation_inner` → `CKDProvider::run_key_generation_client` → `KeyGenerationComputation::compute` → `threshold_signatures::keygen::<BLS12381SHA256, _, _>()`.
4. If `frost_core` internally dispatches `BLS12381SHA256::HID(…)`, every node aborts with `thread 'tokio-runtime-worker' panicked at 'not implemented'`.
5. The key-generation attempt fails; `vote_abort_key_event_instance` is sent; the next attempt repeats identically — the domain is permanently stuck in `Initializing`.

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** crates/threshold-signatures/src/confidential_key_derivation/ciphersuite.rs (L42-90)
```rust
// We are currently not using all the functionality. Therefore,
// I implemented only those that we use.
impl frost_core::Ciphersuite for BLS12381SHA256 {
    const ID: &'static str = CONTEXT_STRING;

    type Group = BLS12381G2Group;

    type HashOutput = [u8; 64];

    type SignatureSerialization = [u8; 64];

    #[allow(unused)]
    fn H1(m: &[u8]) -> <<Self::Group as frost_core::Group>::Field as frost_core::Field>::Scalar {
        unimplemented!()
    }

    #[allow(unused)]
    fn H2(m: &[u8]) -> <<Self::Group as frost_core::Group>::Field as frost_core::Field>::Scalar {
        unimplemented!()
    }

    #[allow(unused)]
    fn H3(m: &[u8]) -> <<Self::Group as frost_core::Group>::Field as frost_core::Field>::Scalar {
        unimplemented!()
    }

    #[allow(unused)]
    fn H4(m: &[u8]) -> Self::HashOutput {
        unimplemented!()
    }

    #[allow(unused)]
    fn H5(_m: &[u8]) -> Self::HashOutput {
        unimplemented!()
    }

    fn HDKG(
        m: &[u8],
    ) -> Option<<<Self::Group as frost_core::Group>::Field as frost_core::Field>::Scalar> {
        Some(hash_to_scalar(&[CONTEXT_STRING.as_bytes(), b"dkg"], m))
    }

    #[allow(unused)]
    fn HID(
        m: &[u8],
    ) -> Option<<<Self::Group as frost_core::Group>::Field as frost_core::Field>::Scalar> {
        unimplemented!()
    }
}
```

**File:** crates/node/src/providers/ckd/key_generation.rs (L33-48)
```rust
    async fn compute(self, channel: &mut NetworkTaskChannel) -> anyhow::Result<KeygenOutput> {
        let cs_participants = channel
            .participants()
            .iter()
            .copied()
            .map(Participant::from)
            .collect::<Vec<_>>();
        let me = channel.my_participant_id();
        let protocol = threshold_signatures::keygen::<BLS12381SHA256, _, _>(
            &cs_participants,
            me.into(),
            self.threshold,
            OsRng,
        )?;
        run_protocol("CKD key generation", channel, protocol).await
    }
```

**File:** crates/node/src/key_events.rs (L58-90)
```rust
    let (keyshare, public_key) = match domain.protocol {
        Protocol::CaitSith => {
            let keyshare =
                EcdsaSignatureProvider::run_key_generation_client(threshold, channel).await?;
            let public_key = dtos::PublicKey::Secp256k1(dtos::Secp256k1PublicKey::try_from(
                keyshare.public_key.to_element().to_affine(),
            )?);
            (KeyshareData::Secp256k1(keyshare), public_key)
        }
        Protocol::DamgardEtAl => {
            let keyshare =
                RobustEcdsaSignatureProvider::run_key_generation_client(threshold, channel).await?;
            let public_key = dtos::PublicKey::Secp256k1(dtos::Secp256k1PublicKey::try_from(
                keyshare.public_key.to_element().to_affine(),
            )?);
            (KeyshareData::Secp256k1(keyshare), public_key)
        }
        Protocol::Frost => {
            let keyshare =
                EddsaSignatureProvider::run_key_generation_client(threshold, channel).await?;
            let public_key = dtos::PublicKey::Ed25519(dtos::Ed25519PublicKey::from(
                keyshare.public_key.to_element().compress(),
            ));
            (KeyshareData::Ed25519(keyshare), public_key)
        }
        Protocol::ConfidentialKeyDerivation => {
            let keyshare = CKDProvider::run_key_generation_client(threshold, channel).await?;
            let public_key = dtos::PublicKey::Bls12381(dtos::Bls12381G2PublicKey::from(
                &keyshare.public_key.to_element(),
            ));
            (KeyshareData::Bls12381(keyshare), public_key)
        }
    };
```

**File:** crates/node/src/providers/ckd.rs (L81-86)
```rust
    async fn run_key_generation_client(
        threshold: ReconstructionThreshold,
        channel: NetworkTaskChannel,
    ) -> anyhow::Result<Self::KeygenOutput> {
        Self::run_key_generation_client_internal(threshold, channel).await
    }
```
