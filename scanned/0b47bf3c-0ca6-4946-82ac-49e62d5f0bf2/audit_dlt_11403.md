# [?] Fix sub-circuit padding & Pk/Vk non-determinisim to prevent variadic circuit sizes (#1064)

## Summary
Severity: Unknown
Chain: ZK
Component: privacy-ethereum/zkevm-circuits
Published: 2023-01-18
Source: https://github.com/privacy-ethereum/zkevm-circuits/commit/98646613d517f473489d7b18d4ea8b53a43b5e11
Type: security-commit

## Details
Fix sub-circuit padding & Pk/Vk non-determinisim to prevent variadic circuit sizes (#1064)

* fix: Include Padding tag for `CopyDataType`

This includes a new tag `Padding` for `CopyDataType` enum which enables
applying conditions when we need to pad the number of copies to be fixed
(ie: avoiding variadic size circuits).

Co-authored-by: Eduard S<eduardsanou@posteo.net>

* fix: Include `max_copy_rows` in `CircuitsParams`

We need some way to set a fixed size for the ammount of rows of copy we
can have in our `CopyCircuit` so that we don't fall into variadic
circuits & also, we can set a hard cap for the padding etc..

Co-authored-by: Eduard S <eduardsanou@posteo.net>

* fix: Introduce padding in the copy_circuit assignation

This includes checks of `CopyDataType::Padding` within the constraints
of the CopyCircuit to enable padding up to
`CircuitsParams::max_copy_rows`.
Also adds assertions to guarantee that the `max_copy_rows` value is
never surpassed during witness assignation.

Finally, it also adds explanations for the `+2` final rows that the
circuit requires due to the `Rotation(2)` usage within it.

Co-authored-by: Eduard S <eduardsanou@posteo.net>

* fix: include variadic-permutation check in CopyCircuit tests

* chore: Remove next_halo2_tag tests from copy_circuit

* chore: Fix rebase conflicts`

* chore: Fix clippy lints

* chore: Apply Han's suggestions

Co-authored-by: Eduard S <eduardsanou@posteo.net>

## Patch
### bus-mapping/src/circuit_input_builder.rs
```diff
@@ -45,6 +45,8 @@ pub struct CircuitsParams {
     pub max_txs: usize,
     /// Maximum number of bytes from all txs calldata in the Tx Circuit
     pub max_calldata: usize,
+    /// Max ammount of rows that the CopyCircuit can have.
+    pub max_copy_rows: usize,
     /// Maximum number of bytes supported in the Bytecode Circuit
     pub max_bytecode: usize,
     // TODO: Rename for consistency
@@ -60,6 +62,9 @@ impl Default for CircuitsParams {
             max_rws: 1000,
             max_txs: 1,
             max_calldata: 256,
+            // TODO: Check whether this value is correct or we should increase/decrease based on
+            // this lib tests
+            max_copy_rows: 1000,
             max_bytecode: 512,
             keccak_padding: None,
         }
```

### bus-mapping/src/circuit_input_builder/execution.rs
```diff
@@ -155,8 +155,11 @@ impl ExecState {
 /// Defines the various source/destination types for a copy event.
 #[derive(Clone, Copy, Debug, PartialEq, Eq, EnumIter)]
 pub enum CopyDataType {
+    /// When we need to pad the Copy rows of the circuit up to a certain maximum
+    /// with rows that are not "useful".
+    Padding = 0,
     /// When the source for the copy event is the bytecode table.
-    Bytecode = 1,
+    Bytecode,
     /// When the source/destination for the copy event is memory.
     Memory,
     /// When the source for the copy event is tx's calldata.
@@ -252,12 +255,12 @@ impl CopyEvent {
                     .checked_sub(self.src_addr)
                     .unwrap_or_default(),
             ),
-            CopyDataType::RlcAcc | CopyDataType::TxLog => unreachable!(),
+            CopyDataType::RlcAcc | CopyDataType::TxLog | CopyDataType::Padding => unreachable!(),
         };
         let destination_rw_increase = match self.dst_type {
             CopyDataType::RlcAcc | CopyDataType::Bytecode => 0,
             CopyDataType::TxLog | CopyDataType::Memory => u64::try_from(step_index).unwrap() / 2,
-            CopyDataType::TxCalldata => unreachable!(),
+            CopyDataType::TxCalldata | CopyDataType::Padding => unreachable!(),
         };
         source_rw_increase + destination_rw_increase
     }
```

### circuit-benchmarks/src/super_circuit.rs
```diff
@@ -71,7 +71,7 @@ mod tests {
 
         block.sign(&wallets);
 
-        let (_, circuit, instance, _) = SuperCircuit::<_, 1, 32, 512>::build(block).unwrap();
+        let (_, circuit, instance, _) = SuperCircuit::<_, 1, 32, 512, 512>::build(block).unwrap();
         let instance_refs: Vec<&[Fr]> = instance.iter().map(|v| &v[..]).collect();
 
         // Bench setup generation
@@ -96,7 +96,7 @@ mod tests {
             Challenge255<G1Affine>,
             ChaChaRng,
             Blake2bWrite<Vec<u8>, G1Affine, Challenge255<G1Affine>>,
-            SuperCircuit<Fr, 1, 32, 512>,
+            SuperCircuit<Fr, 1, 32, 512, 512>,
         >(
             &general_params,
             &pk,
```

### integration-tests/src/integration_test_circuits.rs
```diff
@@ -38,6 +38,7 @@ const CIRCUITS_PARAMS: CircuitsParams = CircuitsParams {
     max_txs: 4,
     max_calldata: 4000,
     max_bytecode: 4000,
+    max_copy_rows: 16384,
     keccak_padding: None,
 };
 
@@ -344,6 +345,7 @@ pub async fn test_super_circuit_block(block_num: u64) {
     const MAX_CALLDATA: usize = 512;
     const MAX_RWS: usize = 5888;
     const MAX_BYTECODE: usize = 5000;
+    const MAX_COPY_ROWS: usize = 5888;
 
     log::info!("test super circuit, block number: {}", block_num);
     let cli = get_client();
@@ -354,14 +356,15 @@ pub async fn test_super_circuit_block(block_num: u64) {
             max_txs: MAX_TXS,
             max_calldata: MAX_CALLDATA,
             max_bytecode: MAX_BYTECODE,
+            max_copy_rows: MAX_COPY_ROWS,
             keccak_padding: None,
         },
     )
     .await
     .unwrap();
     let (builder, _) = cli.gen_inputs(block_num).await.unwrap();
     let (k, circuit, instance) =
-        SuperCircuit::<Fr, MAX_TXS, MAX_CALLDATA, MAX_RWS>::build_from_circuit_input_builder(
+        SuperCircuit::<Fr, MAX_TXS, MAX_CALLDATA, MAX_RWS, MAX_COPY_ROWS>::build_from_circuit_input_builder(
             &builder,
         )
         .unwrap();
```

### integration-tests/tests/circuit_input_builder.rs
```diff
@@ -18,6 +18,7 @@ async fn test_circuit_input_builder_block(block_num: u64) {
             max_txs: 1,
             max_calldata: 4000,
             max_bytecode: 4000,
+            max_copy_rows: 16384,
             keccak_padding: None,
         },
     )
```

### testool/src/statetest/executor.rs
```diff
@@ -287,6 +287,7 @@ pub fn run_test(
             max_rws: 55000,
             max_calldata: 5000,
             max_bytecode: 5000,
+            max_copy_rows: 55000,
             keccak_padding: None,
         };
         let block_data = BlockData::new_from_geth_data_with_params(geth_data, circuits_params);
@@ -312,7 +313,7 @@ pub fn run_test(
         geth_data.sign(&wallets);
 
         let (k, circuit, instance, _builder) =
-            SuperCircuit::<Fr, 1, 32, 255>::build(geth_data).unwrap();
+            SuperCircuit::<Fr, 1, 32, 255, 32>::build(geth_data).unwrap();
         builder = _builder;
 
         let prover = MockProver::run(k, &circuit, instance).unwrap();
```

### zkevm-circuits/src/copy_circuit.rs
```diff
@@ -169,28 +169,34 @@ impl<F: Field> SubCircuitConfig<F> for CopyCircuitConfig<F> {
             let not_last_two_rows = 1.expr()
                 - meta.query_advice(is_last, Rotation::cur())
                 - meta.query_advice(is_last, Rotation::next());
-            cb.condition(not_last_two_rows, |cb| {
-                cb.require_equal(
-                    "rows[0].id == rows[2].id",
-                    meta.query_advice(id, Rotation::cur()),
-                    meta.query_advice(id, Rotation(2)),
-                );
-                cb.require_equal(
-                    "rows[0].tag == rows[2].tag",
-                    tag.value(Rotation::cur())(meta),
-                    tag.value(Rotation(2))(meta),
-                );
-                cb.require_equal(
-                    "rows[0].addr + 1 == rows[2].addr",
-                    meta.query_advice(addr, Rotation::cur()) + 1.expr(),
-                    meta.query_advice(addr, Rotation(2)),
-                );
-                cb.require_equal(
-                    "rows[0].src_addr_end == rows[2].src_addr_end for non-last step",
-                    meta.query_advice(src_addr_end, Rotation::cur()),
-                    meta.query_advice(src_addr_end, Rotation(2)),
-                );
-            });
+            cb.condition(
+                not_last_two_rows
+                    * (not::expr(tag.value_equals(CopyDataType::Padding, Rotation::cur())(
+                        meta,
+                    ))),
+                |cb| {
+                    cb.require_equal(
+                        "rows[0].id == rows[2].id",
+                        meta.query_advice(id, Rotation::cur()),
+                        meta.query_advice(id, Rotation(2)),
+                    );
+                    cb.require_equal(
+                        "rows[0].tag == rows[2].tag",
+                        tag.value(Rotation::cur())(meta),
+                        tag.value(Rotation(2))(meta),
+                    );
+                    cb.require_equal(
+                        "rows[0].addr + 1 == rows[2].addr",
+                        meta.query_advice(addr, Rotation::cur()) + 1.expr(),
+                        meta.query_advice(addr, Rotation(2)),
+                    );
+                    cb.require_equal(
+                        "rows[0].src_addr_end == rows[2].src_addr_end for non-last step",
+                        meta.query_advice(src_addr_end, Rotation::cur()),
+                        meta.query_advice(src_addr_end, Rotation(2)),
+                    );
+                },
+            );
 
             let rw_diff = and::expr([
                 or::expr([
@@ -254,7 +260,10 @@ impl<F: Field> SubCircuitConfig<F> for CopyCircuitConfig<F> {
                 ]),
             );
             cb.condition(
-                not::expr(meta.query_advice(is_last, Rotation::next())),
+                not::expr(meta.query_advice(is_last, Rotation::next()))
+                    * (not::expr(tag.value_equals(CopyDataType::Padding, Rotation::cur())(
+                        meta,
+                    ))),
                 |cb| {
                     cb.require_equal(
                         "bytes_left == bytes_left_next + 1 for non-last step",
@@ -423,6 +432,18 @@ impl<F: Field> CopyCircuitConfig<F> {
         block: &Block<F>,
         challenges: Challenges<Value<F>>,
     ) -> Result<(), Error> {
+        let copy_rows_needed = block
+            .copy_events
+            .iter()
+            .map(|c| c.bytes.len() * 2)
+            .sum::<usize>();
+
+        // The `+ 2` is used to take into account the two extra empty copy rows needed
+        // to satisfy the query at `Rotation(2)` performed inside of the
+        // `rows[2].value == rows[0].value * r + rows[1].value` requirement in the RLC
+        // Accumulation gate.
+        assert!(copy_rows_needed + 2 <= block.circuits_params.max_copy_rows);
+
         let tag_chip = BinaryNumberChip::construct(self.copy_table.tag);
         let lt_chip = LtChip::construct(self.addr_lt_addr_end);
 
@@ -497,11 +518,16 @@ impl<F: Field> CopyCircuitConfig<F> {
                         offset += 1;
                     }
                 }
-                // pad two rows in the end to satisfy Halo2 cell assignment check
-                for _ in 0..2 {
-                    self.assign_padding_row(&mut region, offset, &tag_chip)?;
+
+                for _ in 0..block.circuits_params.max_copy_rows - copy_rows_needed - 2 {
+                    self.assign_padding_row(&mut region, offset, false, &tag_chip, &lt_chip)?;
                     offset += 1;
                 }
+
+                self.assign_padding_row(&mut region, offset, true, &tag_chip, &lt_chip)?;
+                offset += 1;
+                self.assign_padding_row(&mut region, offset, true, &tag_chip, &lt_chip)?;
+
                 Ok(())
             },
         )
@@ -511,15 +537,24 @@ impl<F: Field> CopyCircuitConfig<F> {
         &self,
         region: &mut Region<F>,
         offset: usize,
+        is_last_two: bool,
         tag_chip: &BinaryNumberChip<F, CopyDataType, 3>,
+        lt_chip: &LtChip<F, 8>,
     ) -> Result<(), Error> {
-        // q_enable
-        region.assign_fixed(
-            || "q_enable",
-            self.q_enable,
-            offset,
-            || Value::known(F::zero()),
-        )?;
+        if !is_last_two {
+            // q_enable
+            region.assign_fixed(
+                || "q_enable",
+                self.q_enable,
+                offset,
+                || Value::known(F::one()),
+            )?;
+            // q_step
+            if offset % 2 == 0 {
+                self.q_step.enable(region, offset)?;
+            }
+        }
+
         // is_first
         region.assign_advice(
             || format!("assign is_first {}", offset),
@@ -553,7 +588,7 @@ impl<F: Field> CopyCircuitConfig<F> {
             || format!("assign src_addr_end {}", offset),
             self.copy_table.src_addr_end,
             offset,
-            || Value::known(F::zero()),
+            || Value::known(F::one()),
         )?;
         // bytes_left
         region.assign_advice(
@@ -605,7 +640,10 @@ impl<F: Field> CopyCircuitConfig<F> {
             || Value::known(F::zero()),
         )?;
         // tag
-        tag_chip.assign(region, offset, &CopyDataType::default())?;
+        tag_chip.assign(region, offset, &CopyDataType::Padding)?;
+        // Assing LT gadget
+
+        lt_chip.assign(region, offset, F::zero(), F::one())?;
         Ok(())
     }
 }
@@ -648,8 +686,13 @@ impl<F: Field> SubCircuit<F> for CopyCircuit<F> {
     /// Return the minimum number of rows required to prove the block
     fn min_num_rows_block(block: &witness::Block<F>) -> (usize, usize) {
         (
-            block.copy_events.iter().map(|c| c.bytes.len() * 2).sum(),
-            block.copy_circuit_pad_to,
+            block
+                .copy_events
+                .iter()
+                .map(|c| c.bytes.len() * 2)
+                .sum::<usize>()
+                + 2,
+            block.circuits_params.max_copy_rows,
         )
     }
 
@@ -756,6 +799,8 @@ pub mod dev {
 #[cfg(test)]
 mod tests {
     use super::dev::test_copy_circuit;
+    use crate::evm_circuit::test::rand_bytes;
+    use crate::evm_circuit::witness::block_convert;
     use bus_mapping::evm::{gen_sha3_code, MemoryKind};
     use bus_mapping::{
         circuit_input_builder::{CircuitInputBuilder, CircuitsParams},
@@ -765,9 +810,7 @@ mod tests {
     use halo2_proofs::halo2curves::bn256::Fr;
     use mock::test_ctx::helpers::account_0_code_account_1_no_code;
     use mock::{TestContext, MOCK_ACCOUNTS};
-
-    use crate::evm_circuit::test::rand_bytes;
-    use crate::evm_circuit::witness::block_convert;
+    use pretty_assertions::assert_eq;
 
     fn gen_calldatacopy_data() -> CircuitInputBuilder {
         let length = 0x0fffusize;
@@ -796,6 +839,7 @@ mod tests {
             block.clone(),
             CircuitsParams {
                 max_rws: 8192,
+                max_copy_rows: 8192 + 2,
                 ..Default::default()
             },
         )
@@ -867,6 +911,7 @@ mod tests {
             block.clone(),
             CircuitsParams {
                 max_rws: 2000,
+                max_copy_rows: 0x200 * 2 + 2,
                 ..Default::default()
             },
         )
```

### zkevm-circuits/src/super_circuit.rs
```diff
@@ -111,6 +111,7 @@ pub struct SuperCircuit<
     const MAX_TXS: usize,
     const MAX_CALLDATA: usize,
     const MAX_RWS: usize,
+    const MAX_COPY_ROWS: usize,
 > {
     /// EVM Circuit
     pub evm_circuit: EvmCircuit<F>,
@@ -130,8 +131,13 @@ pub struct SuperCircuit<
     pub keccak_circuit: KeccakCircuit<F>,
 }
 
-impl<F: Field, const MAX_TXS: usize, const MAX_CALLDATA: usize, const MAX_RWS: usize>
-    SuperCircuit<F, MAX_TXS, MAX_CALLDATA, MAX_RWS>
+impl<
+        F: Field,
+        const MAX_TXS: usize,
+        const MAX_CALLDATA: usize,
+        const MAX_RWS: usize,
+        const MAX_COPY_ROWS: usize,
+    > SuperCircuit<F, MAX_TXS, MAX_CALLDATA, MAX_RWS, MAX_COPY_ROWS>
 {
     /// Return the number of rows required to verify a given block
     pub fn get_num_rows_required(block: &Block<F>) -> usize {
@@ -145,8 +151,13 @@ impl<F: Field, const MAX_TXS: usize, const MAX_CALLDATA: usize, const MAX_RWS: u
     }
 }
 
-impl<F: Field, const MAX_TXS: usize, const MAX_CALLDATA: usize, const MAX_RWS: usize> Circuit<F>
-    for SuperCircuit<F, MAX_TXS, MAX_CALLDATA, MAX_RWS>
+impl<
+        F: Field,
+        const MAX_TXS: usize,
+        const MAX_CALLDATA: usize,
+        const MAX_RWS: usize,
+        const MAX_COPY_ROWS: usize,
+    > Circuit<F> for SuperCircuit<F, MAX_TXS, MAX_CALLDATA, MAX_RWS, MAX_COPY_ROWS>
 {
     type Config = SuperCircuitConfig<F, MAX_TXS, MAX_CALLDATA, MAX_RWS>;
     type FloorPlanner = SimpleFloorPlanner;
@@ -305,8 +316,13 @@ impl<F: Field, const MAX_TXS: usize, const MAX_CALLDATA: usize, const MAX_RWS: u
     }
 }
 
-impl<F: Field, const MAX_TXS: usize, const MAX_CALLDATA: usize, const MAX_RWS: usize>
-    SuperCircuit<F, MAX_TXS, MAX_CALLDATA, MAX_RWS>
+impl<
+        F: Field,
+        const MAX_TXS: usize,
+        const MAX_CALLDATA: usize,
+        const MAX_RWS: usize,
+        const MAX_COPY_ROWS: usize,
+    > SuperCircuit<F, MAX_TXS, MAX_CALLDATA, MAX_RWS, MAX_COPY_ROWS>
 {
     /// From the witness data, generate a SuperCircuit instance with all of the
     /// sub-circuits filled with their corresponding witnesses.
@@ -323,6 +339,7 @@ impl<F: Field, const MAX_TXS: usize, const MAX_CALLDATA: usize, const MAX_RWS: u
                 max_txs: MAX_TXS,
                 max_calldata: MAX_CALLDATA,
                 max_rws: MAX_RWS,
+                max_copy_rows: MAX_COPY_ROWS,
                 max_bytecode: 512,
                 keccak_padding: None,
             },
@@ -361,7 +378,7 @@ impl<F: Field, const MAX_TXS: usize, const MAX_CALLDATA: usize, const MAX_RWS: u
         let exp_circuit = ExpCircuit::new_from_block(&block);
         let keccak_circuit = KeccakCircuit::new_from_block(&block);
 
-        let circuit = SuperCircuit::<_, MAX_TXS, MAX_CALLDATA, MAX_RWS> {
+        let circuit = SuperCircuit::<_, MAX_TXS, MAX_CALLDATA, MAX_RWS, MAX_COPY_ROWS> {
             evm_circuit,
             state_circuit,
             tx_circuit,
@@ -423,17 +440,23 @@ mod super_circuit_tests {
     #[test]
     fn super_circuit_degree() {
         let mut cs = ConstraintSystem::<Fr>::default();
-        SuperCircuit::<_, 1, 32, 256>::configure(&mut cs);
+        SuperCircuit::<_, 1, 32, 256, 32>::configure(&mut cs);
         log::info!("super circuit degree: {}", cs.degree());
         log::info!("super circuit minimum_rows: {}", cs.minimum_rows());
         assert!(cs.degree() <= 9);
     }
 
-    fn test_super_circuit<const MAX_TXS: usize, const MAX_CALLDATA: usize, const MAX_RWS: usize>(
+    fn test_super_circuit<
+        const MAX_TXS: usize,
+        const MAX_CALLDATA: usize,
+        const MAX_RWS: usize,
+        const MAX_COPY_ROWS: usize,
+    >(
         block: GethData,
     ) {
         let (k, circuit, instance, _) =
-            SuperCircuit::<Fr, MAX_TXS, MAX_CALLDATA, MAX_RWS>::build(block).unwrap();
+            SuperCircuit::<Fr, MAX_TXS, MAX_CALLDATA, MAX_RWS, MAX_COPY_ROWS>::build(block)
+                .unwrap();
         let prover = MockProver::run(k, &circuit, instance).unwrap();
         let res = prover.verify_par();
         if let Err(err) = res {
@@ -537,7 +560,8 @@ mod super_circuit_tests {
         const MAX_TXS: usize = 1;
         const MAX_CALLDATA: usize = 32;
         const MAX_RWS: usize = 256;
-        test_super_circuit::<MAX_TXS, MAX_CALLDATA, MAX_RWS>(block);
+        const MAX_COPY_ROWS: usize = 256;
+        test_super_circuit::<MAX_TXS, MAX_CALLDATA, MAX_RWS, MAX_COPY_ROWS>(block);
     }
     #[ignore]
     #[test]
@@ -546,7 +570,8 @@ mod super_circuit_tests {
         const MAX_TXS: usize = 2;
         const MAX_CALLDATA: usize = 32;
         const MAX_RWS: usize = 256;
-        test_super_circuit::<MAX_TXS, MAX_CALLDATA, MAX_RWS>(block);
+        const MAX_COPY_ROWS: usize = 256;
+        test_super_circuit::<MAX_TXS, MAX_CALLDATA, MAX_RWS, MAX_COPY_ROWS>(block);
     }
     #[ignore]
     #[test]
@@ -555,6 +580,7 @@ mod super_circuit_tests {
         const MAX_TXS: usize = 2;
         const MAX_CALLDATA: usize = 32;
         const MAX_RWS: usize = 256;
-        test_super_circuit::<MAX_TXS, MAX_CALLDATA, MAX_RWS>(block);
+        const MAX_COPY_ROWS: usize = 256;
+        test_super_circuit::<MAX_TXS, MAX_CALLDATA, MAX_RWS, MAX_COPY_ROWS>(block);
     }
 }
```

### zkevm-circuits/src/witness/block.rs
```diff
@@ -41,8 +41,6 @@ pub struct Block<F> {
     pub evm_circuit_pad_to: usize,
     /// Pad exponentiation circuit to make selectors fixed.
     pub exp_circuit_pad_to: usize,
-    /// Pad copy circuit to make selectors fixed.
-    pub copy_circuit_pad_to: usize,
     /// Circuit Setup Parameters
     pub circuits_params: CircuitsParams,
     /// Inputs to the SHA3 opcode
@@ -203,7 +201,6 @@ pub fn block_convert<F: Field>(
         circuits_params: block.circuits_params.clone(),
         evm_circuit_pad_to: <usize>::default(),
         exp_circuit_pad_to: <usize>::default(),
-        copy_circuit_pad_to: <usize>::default(),
         prev_state_root: block.prev_state_root,
         keccak_inputs: circuit_input_builder::keccak_inputs(block, code_db)?,
         eth_block: block.eth_block.clone(),
```
