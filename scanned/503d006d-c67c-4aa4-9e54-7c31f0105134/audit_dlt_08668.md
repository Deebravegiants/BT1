# [?] Test zk proof validation exploit

## Summary
Severity: Unknown
Chain: Namada
Component: namada-net/namada
Published: 2026-08-06
Source: https://github.com/namada-net/namada/commit/24d5490cf79828cabcbd48aa6f5dd72256cca1b7
Type: security-commit

## Details
Test zk proof validation exploit

## Patch
### crates/shielded_token/src/validation.rs
```diff
@@ -369,3 +369,329 @@ pub mod testing {
         }
     }
 }
+
+#[cfg(all(test, not(feature = "testing")))]
+mod tests {
+    use std::ops::AddAssign;
+    use std::sync::Mutex;
+
+    use masp_primitives::asset_type::AssetType;
+    use masp_primitives::consensus::{BlockHeight, TestNetwork as Network};
+    use masp_primitives::constants::{
+        spending_key_generator, value_commitment_randomness_generator,
+    };
+    use masp_primitives::convert::AllowedConversion;
+    use masp_primitives::group::GroupEncoding;
+    use masp_primitives::group::prime::PrimeCurveAffine;
+    use masp_primitives::memo::MemoBytes;
+    use masp_primitives::merkle_tree::MerklePath;
+    use masp_primitives::sapling::prover::TxProver;
+    use masp_primitives::sapling::redjubjub::{
+        PrivateKey, PublicKey, Signature,
+    };
+    use masp_primitives::sapling::{Diversifier, Node, PaymentAddress, Rseed};
+    use masp_primitives::transaction::TransparentAddress;
+    use masp_primitives::transaction::builder::Builder;
+    use masp_primitives::transaction::components::sapling::builder::RngBuildParams;
+    use masp_primitives::transaction::components::{
+        GROTH_PROOF_SIZE, I128Sum, TxOut, U64Sum,
+    };
+    use masp_primitives::transaction::fees::fixed::FeeRule;
+    use masp_primitives::zip32::{
+        ExtendedFullViewingKey, ExtendedSpendingKey, PseudoExtendedKey,
+    };
+    use masp_primitives::{bls12_381, jubjub};
+    use masp_proofs::bellman::groth16::Proof;
+    use masp_proofs::bls12_381::{Bls12, G1Affine, G2Affine};
+    use rand_core::{CryptoRng, OsRng, RngCore};
+
+    use super::{
+        CONVERT_NAME, OUTPUT_NAME, SPEND_NAME, get_params_dir,
+        preload_verifying_keys, verify_shielded_tx,
+    };
+    use crate::Error;
+
+    fn find_valid_diversifier<R: RngCore + CryptoRng>(
+        rng: &mut R,
+    ) -> (Diversifier, jubjub::SubgroupPoint) {
+        let mut diversifier;
+        let g_d;
+        loop {
+            let mut d = [0; 11];
+            rng.fill_bytes(&mut d);
+            diversifier = Diversifier(d);
+            if let Some(val) = diversifier.g_d() {
+                g_d = val;
+                break;
+            }
+        }
+        (diversifier, g_d)
+    }
+
+    fn masp_compute_value_balance(
+        asset_type: AssetType,
+        value: i128,
+    ) -> Option<jubjub::ExtendedPoint> {
+        let abs = match value.checked_abs() {
+            Some(a) => a as u128,
+            None => return None,
+        };
+        let is_negative = value.is_negative();
+        let mut abs_bytes = [0u8; 32];
+        abs_bytes[0..16].copy_from_slice(&abs.to_le_bytes());
+        let mut value_balance = asset_type.value_commitment_generator()
+            * jubjub::Fr::from_bytes(&abs_bytes).unwrap();
+        if is_negative {
+            value_balance = -value_balance;
+        }
+        Some(value_balance.into())
+    }
+
+    struct SaplingProvingContext {
+        bsk: jubjub::Fr,
+        cv_sum: jubjub::ExtendedPoint,
+    }
+
+    struct MockTxProver<R: RngCore>(Mutex<R>);
+
+    impl<R: RngCore> TxProver for MockTxProver<R> {
+        type SaplingProvingContext = SaplingProvingContext;
+
+        fn new_sapling_proving_context(&self) -> Self::SaplingProvingContext {
+            SaplingProvingContext {
+                bsk: jubjub::Fr::zero(),
+                cv_sum: jubjub::ExtendedPoint::identity(),
+            }
+        }
+
+        fn spend_proof(
+            &self,
+            ctx: &mut Self::SaplingProvingContext,
+            proof_generation_key: masp_primitives::sapling::ProofGenerationKey,
+            _diversifier: Diversifier,
+            _rseed: Rseed,
+            ar: jubjub::Fr,
+            asset_type: AssetType,
+            value: u64,
+            _anchor: bls12_381::Scalar,
+            _merkle_path: MerklePath<Node>,
+            rcv: jubjub::Fr,
+        ) -> Result<
+            ([u8; GROTH_PROOF_SIZE], jubjub::ExtendedPoint, PublicKey),
+            (),
+        > {
+            {
+                let mut tmp = rcv;
+                tmp.add_assign(&ctx.bsk);
+                ctx.bsk = tmp;
+            }
+            let value_commitment = asset_type.value_commitment(value, rcv);
+            let rk = PublicKey(proof_generation_key.ak.into())
+                .randomize(ar, spending_key_generator());
+            let value_commitment: jubjub::ExtendedPoint =
+                value_commitment.commitment().into();
+            ctx.cv_sum += value_commitment;
+            let mut zkproof = [0u8; GROTH_PROOF_SIZE];
+            let proof = Proof::<Bls12> {
+                a: G1Affine::generator(),
+                b: G2Affine::generator(),
+                c: G1Affine::generator(),
+            };
+            proof
+                .write(&mut zkproof[..])
+                .expect("should be able to serialize a proof");
+            Ok((zkproof, value_commitment, rk))
+        }
+
+        fn output_proof(
+            &self,
+            ctx: &mut Self::SaplingProvingContext,
+            _esk: jubjub::Fr,
+            _payment_address: PaymentAddress,
+            _rcm: jubjub::Fr,
+            asset_type: AssetType,
+            value: u64,
+            rcv: jubjub::Fr,
+        ) -> ([u8; GROTH_PROOF_SIZE], jubjub::ExtendedPoint) {
+            {
+                let mut tmp = rcv.neg();
+                tmp.add_assign(&ctx.bsk);
+                ctx.bsk = tmp;
+            }
+            let value_commitment = asset_type.value_commitment(value, rcv);
+            let value_commitment_point: jubjub::ExtendedPoint =
+                value_commitment.commitment().into();
+            ctx.cv_sum -= value_commitment_point;
+            let mut zkproof = [0u8; GROTH_PROOF_SIZE];
+            let proof = Proof::<Bls12> {
+                a: G1Affine::generator(),
+                b: G2Affine::generator(),
+                c: G1Affine::generator(),
+            };
+            proof
+                .write(&mut zkproof[..])
+                .expect("should be able to serialize a proof");
+            (zkproof, value_commitment_point)
+        }
+
+        fn convert_proof(
+            &self,
+            ctx: &mut Self::SaplingProvingContext,
+            allowed_conversion: AllowedConversion,
+            value: u64,
+            _anchor: bls12_381::Scalar,
+            _merkle_path: MerklePath<Node>,
+            rcv: jubjub::Fr,
+        ) -> Result<([u8; GROTH_PROOF_SIZE], jubjub::ExtendedPoint), ()>
+        {
+            {
+                let mut tmp = rcv;
+                tmp.add_assign(&ctx.bsk);
+                ctx.bsk = tmp;
+            }
+            let value_commitment =
+                allowed_conversion.value_commitment(value, rcv);
+            let value_commitment: jubjub::ExtendedPoint =
+                value_commitment.commitment().into();
+            ctx.cv_sum += value_commitment;
+            let mut zkproof = [0u8; GROTH_PROOF_SIZE];
+            let proof = Proof::<Bls12> {
+                a: G1Affine::generator(),
+                b: G2Affine::generator(),
+                c: G1Affine::generator(),
+            };
+            proof
+                .write(&mut zkproof[..])
+                .expect("should be able to serialize a proof");
+            Ok((zkproof, value_commitment))
+        }
+
+        fn binding_sig(
+            &self,
+            ctx: &mut Self::SaplingProvingContext,
+            assets_and_values: &I128Sum,
+            sighash: &[u8; 32],
+        ) -> Result<Signature, ()> {
+            let mut rng = self.0.lock().unwrap();
+            let bsk = PrivateKey(ctx.bsk);
+            let bvk = PublicKey::from_private(
+                &bsk,
+                value_commitment_randomness_generator(),
+            );
+            {
+                let final_bvk = assets_and_values
+                    .components()
+                    .map(|(asset_type, value_balance)| {
+                        masp_compute_value_balance(*asset_type, *value_balance)
+                    })
+                    .try_fold(ctx.cv_sum, |tmp, value_balance| {
+                        Result::<_, ()>::Ok(tmp - value_balance.ok_or(())?)
+                    })?;
+                if bvk.0 != final_bvk {
+                    return Err(());
+                }
+            }
+            let mut data_to_be_signed = [0u8; 64];
+            data_to_be_signed[0..32].copy_from_slice(&bvk.0.to_bytes());
+            data_to_be_signed[32..64].copy_from_slice(&sighash[..]);
+            Ok(bsk.sign(
+                &data_to_be_signed,
+                &mut *rng,
+                value_commitment_randomness_generator(),
+            ))
+        }
+    }
+
+    /// Ensure MASP parameters are present on disk, downloading them if
+    /// necessary.
+    fn ensure_masp_params() {
+        let params_dir = get_params_dir();
+        let spend_path = params_dir.join(SPEND_NAME);
+        let convert_path = params_dir.join(CONVERT_NAME);
+        let output_path = params_dir.join(OUTPUT_NAME);
+        if !spend_path.exists()
+            || !convert_path.exists()
+            || !output_path.exists()
+        {
+            masp_proofs::download_masp_parameters(None)
+                .expect("download MASP parameters");
+        }
+    }
+
+    /// Regression test for the `masp_proofs` 3.0.8 bug where `BatchValidator`
+    /// accepts any proof whose elements are valid curve points, even if the
+    /// proof does not satisfy the Groth16 verification equation.
+    ///
+    /// A shielded transaction is built with fake ZK proofs (generator
+    /// elements) but real value commitments and binding signatures.
+    /// `verify_shielded_tx` must reject it with "Invalid proofs or
+    /// signatures".
+    #[test]
+    fn test_verify_shielded_tx_rejects_fake_zk_proofs() {
+        ensure_masp_params();
+        preload_verifying_keys();
+
+        let mut rng = OsRng;
+
+        // Generate a spending key and derive a payment address
+        let mut seed = [0u8; 32];
+        rng.fill_bytes(&mut seed);
+        let spending_key = ExtendedSpendingKey::master(&seed);
+        let viewing_key = ExtendedFullViewingKey::from(&spending_key).fvk.vk;
+        let (div, _g_d) = find_valid_diversifier(&mut rng);
+        let payment_addr = viewing_key
+            .to_payment_address(div)
+            .expect("a PaymentAddress");
+
+        // Create an asset type and transparent address
+        let asset_type =
+            AssetType::new(b"test_token").expect("valid asset type");
+        let address = TransparentAddress([12u8; 20]);
+        let value: u64 = 100;
+
+        // Build a shielding transaction: transparent input -> sapling output
+        let mut builder = Builder::<Network, PseudoExtendedKey>::new(
+            Network,
+            BlockHeight::from_u32(1),
+        );
+        builder
+            .add_transparent_input(TxOut {
+                asset_type,
+                value,
+                address,
+            })
+            .unwrap();
+        builder
+            .add_sapling_output(
+                None,
+                payment_addr,
+                asset_type,
+                value,
+                MemoBytes::empty(),
+            )
+            .unwrap();
+
+        let prover = MockTxProver(Mutex::new(OsRng));
+        let (transaction, _metadata) = builder
+            .build(
+                &prover,
+                &FeeRule::non_standard(U64Sum::zero()),
+                &mut rng,
+                &mut RngBuildParams::new(OsRng),
+            )
+            .expect("build transaction");
+
+        // verify_shielded_tx must reject the fake ZK proofs
+        let result = verify_shielded_tx(&transaction, |_| Ok(()));
+
+        assert!(
+            matches!(
+                result,
+                Err(Error::SimpleMessage("Invalid proofs or signatures"))
+            ),
+            "Expected verify_shielded_tx to reject fake ZK proofs with \
+             \"Invalid proofs or signatures\", got: {:?}",
+            result
+        );
+    }
+}
```
