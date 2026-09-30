# [?] Improve cost safety, prevent overflows

## Summary
Severity: Unknown
Chain: Aleo
Component: AleoNet/snarkVM-test
Published: 2024-01-27
Source: https://github.com/AleoNet/snarkVM-test/commit/48ab38b7e0c7a0e80582517456dc6c84237e9462
Type: security-commit

## Details
Improve cost safety, prevent overflows

## Patch
### synthesizer/src/vm/helpers/cost.rs
```diff
@@ -22,15 +22,16 @@ use console::{
 };
 use ledger_block::{Deployment, Execution};
 use ledger_store::ConsensusStorage;
-use synthesizer_program::{CastType, Command, Instruction, Operand, StackProgram};
+use synthesizer_program::{CastType, Command, Finalize, Instruction, Operand, StackProgram};
 
-// Finalize costs for compute heavy operations. Used as BASE_COST + PER_BYTE_COST * SIZE_IN_BYTES.
+// Finalize costs for compute heavy operations, derived as:
+// `BASE_COST + (PER_BYTE_COST * SIZE_IN_BYTES)`.
 
-const CAST_COMMAND_BASE_COST: u64 = 500;
+const CAST_BASE_COST: u64 = 500;
 const CAST_PER_BYTE_COST: u64 = 30;
 
-const GET_COMMAND_BASE_COST: u64 = 10_000;
-const GET_COMMAND_PER_BYTE_COST: u64 = 10;
+const MAPPING_BASE_COST: u64 = 10_000;
+const MAPPING_PER_BYTE_COST: u64 = 10;
 
 const HASH_BASE_COST: u64 = 10_000;
 const HASH_PER_BYTE_COST: u64 = 30;
@@ -41,8 +42,8 @@ const HASH_BHP_PER_BYTE_COST: u64 = 300;
 const HASH_PSD_BASE_COST: u64 = 40_000;
 const HASH_PSD_PER_BYTE_COST: u64 = 75;
 
-const SET_COMMAND_BASE_COST: u64 = 10_000;
-const SET_COMMAND_PER_BYTE_COST: u64 = 100;
+const SET_BASE_COST: u64 = 10_000;
+const SET_PER_BYTE_COST: u64 = 100;
 
 /// Returns the *minimum* cost in microcredits to publish the given deployment (total cost, (storage cost, namespace cost)).
 pub fn deployment_cost<N: Network>(deployment: &Deployment<N>) -> Result<(u64, (u64, u64))> {
@@ -106,35 +107,72 @@ pub fn execution_cost<N: Network, C: ConsensusStorage<N>>(
 
 /// Returns the minimum number of microcredits required to run the finalize.
 pub fn cost_in_microcredits<N: Network>(stack: &Stack<N>, function_name: &Identifier<N>) -> Result<u64> {
+    /// A helper function to determine the plaintext type in bytes.
+    fn plaintext_size_in_bytes<N: Network>(stack: &Stack<N>, plaintext_type: &PlaintextType<N>) -> Result<u64> {
+        match plaintext_type {
+            PlaintextType::Literal(literal_type) => Ok(literal_type.size_in_bytes::<N>() as u64),
+            PlaintextType::Struct(struct_name) => {
+                // Retrieve the struct from the stack.
+                let struct_ = stack.program().get_struct(struct_name)?;
+                // Retrieve the size of the struct name.
+                let size_of_name = struct_.name().to_bytes_le()?.len() as u64;
+                // Retrieve the size of all the members of the struct.
+                let size_of_members = struct_.members().iter().try_fold(0u64, |acc, (_, member_type)| {
+                    acc.checked_add(plaintext_size_in_bytes(stack, member_type)?).ok_or(anyhow!(
+                        "Overflowed while computing the size of the struct '{}/{struct_name}' - {member_type}",
+                        stack.program_id()
+                    ))
+                })?;
+                // Return the size of the struct.
+                Ok(size_of_name.saturating_add(size_of_members))
+            }
+            PlaintextType::Array(array_type) => {
+                // Retrieve the number of elements in the array.
+                let num_elements = **array_type.length() as u64;
+                // Compute the size of an array element.
+                let size_of_element = plaintext_size_in_bytes(stack, array_type.next_element_type())?;
+                // Return the size of the array.
+                Ok(num_elements.saturating_mul(size_of_element))
+            }
+        }
+    }
+
+    /// A helper function to compute the following: base_cost + (byte_multiplier * size_of_operands).
+    fn cost_in_size<'a, N: Network>(
+        stack: &Stack<N>,
+        finalize: &Finalize<N>,
+        operands: impl IntoIterator<Item = &'a Operand<N>>,
+        byte_multiplier: u64,
+        base_cost: u64,
+    ) -> Result<u64> {
+        // Retrieve the finalize types.
+        let finalize_types = stack.get_finalize_types(finalize.name())?;
+        // Compute the size of the operands.
+        let size_of_operands = operands.into_iter().try_fold(0u64, |acc, operand| {
+            // Determine the size of the operand.
+            let operand_size = match finalize_types.get_type_from_operand(stack, operand)? {
+                FinalizeType::Plaintext(plaintext_type) => plaintext_size_in_bytes(stack, &plaintext_type)?,
+                FinalizeType::Future(future) => {
+                    bail!("Future '{future}' is not a valid operand in the finalize scope");
+                }
+            };
+            // Safely add the size to the accumulator.
+            acc.checked_add(operand_size).ok_or(anyhow!(
+                "Overflowed while computing the size of the operand '{operand}' in '{}/{}' (finalize)",
+                stack.program_id(),
+                finalize.name()
+            ))
+        })?;
+        // Return the cost.
+        Ok(base_cost.saturating_add(byte_multiplier.saturating_mul(size_of_operands)))
+    }
+
     // Retrieve the finalize logic.
     let Some(finalize) = stack.get_function_ref(function_name)?.finalize_logic() else {
         // Return a finalize cost of 0, if the function does not have a finalize scope.
         return Ok(0);
     };
 
-    // Retrieve the finalize types.
-    let finalize_types = stack.get_finalize_types(finalize.name())?;
-
-    // Helper function to get the size of the operand type.
-    let operand_size_in_bytes = |operand: &Operand<N>| {
-        // Get the finalize type from the operand.
-        let finalize_type = finalize_types.get_type_from_operand(stack, operand)?;
-
-        // Get the plaintext type from the finalize type.
-        let plaintext_type = match finalize_type {
-            FinalizeType::Plaintext(plaintext_type) => plaintext_type,
-            FinalizeType::Future(_) => bail!("`Future` types are not supported in storage cost computation."),
-        };
-
-        // Get the size of the operand type.
-        plaintext_size_in_bytes(stack, &plaintext_type)
-    };
-
-    let size_cost = |operands: &[Operand<N>], byte_multiplier: u64, base_cost: u64| {
-        let operand_size = operands.iter().map(operand_size_in_bytes).sum::<Result<u64>>()?;
-        Ok(base_cost.saturating_add(operand_size.saturating_mul(byte_multiplier)))
-    };
-
     // Measure the cost of each command.
     let cost = |command: &Command<N>| match command {
         Command::Instruction(Instruction::Abs(_)) => Ok(500),
@@ -154,7 +192,7 @@ pub fn cost_in_microcredits<N: Network>(stack: &Stack<N>, function_name: &Identi
                 CastType::Plaintext(PlaintextType::Literal(_)) => Ok(500),
                 CastType::Plaintext(plaintext_type) => Ok(plaintext_size_in_bytes(stack, plaintext_type)?
                     .saturating_mul(CAST_PER_BYTE_COST)
-                    .saturating_add(CAST_COMMAND_BASE_COST)),
+                    .saturating_add(CAST_BASE_COST)),
                 _ => Ok(500),
             }
         }
@@ -166,32 +204,34 @@ pub fn cost_in_microcredits<N: Network>(stack: &Stack<N>, function_name: &Identi
                 CastType::Plaintext(PlaintextType::Literal(_)) => Ok(500),
                 CastType::Plaintext(plaintext_type) => Ok(plaintext_size_in_bytes(stack, plaintext_type)?
                     .saturating_mul(CAST_PER_BYTE_COST)
-                    .saturating_add(CAST_COMMAND_BASE_COST)),
+                    .saturating_add(CAST_BASE_COST)),
                 _ => Ok(500),
             }
         }
         Command::Instruction(Instruction::CommitBHP256(commit)) => {
-            size_cost(commit.operands(), HASH_BHP_PER_BYTE_COST, HASH_BHP_BASE_COST)
+            cost_in_size(stack, finalize, commit.operands(), HASH_BHP_PER_BYTE_COST, HASH_BHP_BASE_COST)
         }
         Command::Instruction(Instruction::CommitBHP512(commit)) => {
-            size_cost(commit.operands(), HASH_BHP_PER_BYTE_COST, HASH_BHP_BASE_COST)
+            cost_in_size(stack, finalize, commit.operands(), HASH_BHP_PER_BYTE_COST, HASH_BHP_BASE_COST)
         }
         Command::Instruction(Instruction::CommitBHP768(commit)) => {
-            size_cost(commit.operands(), HASH_BHP_PER_BYTE_COST, HASH_BHP_BASE_COST)
+            cost_in_size(stack, finalize, commit.operands(), HASH_BHP_PER_BYTE_COST, HASH_BHP_BASE_COST)
         }
         Command::Instruction(Instruction::CommitBHP1024(commit)) => {
-            size_cost(commit.operands(), HASH_BHP_PER_BYTE_COST, HASH_BHP_BASE_COST)
+            cost_in_size(stack, finalize, commit.operands(), HASH_BHP_PER_BYTE_COST, HASH_BHP_BASE_COST)
         }
         Command::Instruction(Instruction::CommitPED64(commit)) => {
-            size_cost(commit.operands(), HASH_PER_BYTE_COST, HASH_BASE_COST)
+            cost_in_size(stack, finalize, commit.operands(), HASH_PER_BYTE_COST, HASH_BASE_COST)
         }
         Command::Instruction(Instruction::CommitPED128(commit)) => {
-            size_cost(commit.operands(), HASH_PER_BYTE_COST, HASH_BASE_COST)
+            cost_in_size(stack, finalize, commit.operands(), HASH_PER_BYTE_COST, HASH_BASE_COST)
         }
         Command::Instruction(Instruction::Div(div)) => {
             let operands = div.operands();
             ensure!(operands.len() == 2, "div opcode must have exactly two operands.");
 
+            // Retrieve the finalize types.
+            let finalize_types = stack.get_finalize_types(finalize.name())?;
             // Get the price by operand type.
             let operand_type = finalize_types.get_type_from_operand(stack, &operands[0])?;
             match operand_type {
@@ -207,49 +247,49 @@ pub fn cost_in_microcredits<N: Network>(stack: &Stack<N>, function_name: &Identi
         Command::Instruction(Instruction::GreaterThan(_)) => Ok(500),
         Command::Instruction(Instruction::GreaterThanOrEqual(_)) => Ok(500),
         Command::Instruction(Instruction::HashBHP256(hash)) => {
-            size_cost(hash.operands(), HASH_BHP_PER_BYTE_COST, HASH_BHP_BASE_COST)
+            cost_in_size(stack, finalize, hash.operands(), HASH_BHP_PER_BYTE_COST, HASH_BHP_BASE_COST)
         }
         Command::Instruction(Instruction::HashBHP512(hash)) => {
-            size_cost(hash.operands(), HASH_BHP_PER_BYTE_COST, HASH_BHP_BASE_COST)
+            cost_in_size(stack, finalize, hash.operands(), HASH_BHP_PER_BYTE_COST, HASH_BHP_BASE_COST)
         }
         Command::Instruction(Instruction::HashBHP768(hash)) => {
-            size_cost(hash.operands(), HASH_BHP_PER_BYTE_COST, HASH_BHP_BASE_COST)
+            cost_in_size(stack, finalize, hash.operands(), HASH_BHP_PER_BYTE_COST, HASH_BHP_BASE_COST)
         }
         Command::Instruction(Instruction::HashBHP1024(hash)) => {
-            size_cost(hash.operands(), HASH_BHP_PER_BYTE_COST, HASH_BHP_BASE_COST)
+            cost_in_size(stack, finalize, hash.operands(), HASH_BHP_PER_BYTE_COST, HASH_BHP_BASE_COST)
         }
         Command::Instruction(Instruction::HashKeccak256(hash)) => {
-            size_cost(hash.operands(), HASH_PER_BYTE_COST, HASH_BASE_COST)
+            cost_in_size(stack, finalize, hash.operands(), HASH_PER_BYTE_COST, HASH_BASE_COST)
         }
         Command::Instruction(Instruction::HashKeccak384(hash)) => {
-            size_cost(hash.operands(), HASH_PER_BYTE_COST, HASH_BASE_COST)
+            cost_in_size(stack, finalize, hash.operands(), HASH_PER_BYTE_COST, HASH_BASE_COST)
         }
         Command::Instruction(Instruction::HashKeccak512(hash)) => {
-            size_cost(hash.operands(), HASH_PER_BYTE_COST, HASH_BASE_COST)
+            cost_in_size(stack, finalize, hash.operands(), HASH_PER_BYTE_COST, HASH_BASE_COST)
         }
         Command::Instruction(Instruction::HashPED64(hash)) => {
-            size_cost(hash.operands(), HASH_PER_BYTE_COST, HASH_BASE_COST)
+            cost_in_size(stack, finalize, hash.operands(), HASH_PER_BYTE_COST, HASH_BASE_COST)
         }
         Command::Instruction(Instruction::HashPED128(hash)) => {
-            size_cost(hash.operands(), HASH_PER_BYTE_COST, HASH_BASE_COST)
+            cost_in_size(stack, finalize, hash.operands(), HASH_PER_BYTE_COST, HASH_BASE_COST)
         }
         Command::Instruction(Instruction::HashPSD2(hash)) => {
-            size_cost(hash.operands(), HASH_PSD_PER_BYTE_COST, HASH_PSD_BASE_COST)
+            cost_in_size(stack, finalize, hash.operands(), HASH_PSD_PER_BYTE_COST, HASH_PSD_BASE_COST)
         }
         Command::Instruction(Instruction::HashPSD4(hash)) => {
-            size_cost(hash.operands(), HASH_PSD_PER_BYTE_COST, HASH_PSD_BASE_COST)
+            cost_in_size(stack, finalize, hash.operands(), HASH_PSD_PER_BYTE_COST, HASH_PSD_BASE_COST)
         }
         Command::Instruction(Instruction::HashPSD8(hash)) => {
-            size_cost(hash.operands(), HASH_PSD_PER_BYTE_COST, HASH_PSD_BASE_COST)
+            cost_in_size(stack, finalize, hash.operands(), HASH_PSD_PER_BYTE_COST, HASH_PSD_BASE_COST)
         }
         Command::Instruction(Instruction::HashSha3_256(hash)) => {
-            size_cost(hash.operands(), HASH_PER_BYTE_COST, HASH_BASE_COST)
+            cost_in_size(stack, finalize, hash.operands(), HASH_PER_BYTE_COST, HASH_BASE_COST)
         }
         Command::Instruction(Instruction::HashSha3_384(hash)) => {
-            size_cost(hash.operands(), HASH_PER_BYTE_COST, HASH_BASE_COST)
+            cost_in_size(stack, finalize, hash.operands(), HASH_PER_BYTE_COST, HASH_BASE_COST)
         }
         Command::Instruction(Instruction::HashSha3_512(hash)) => {
-            size_cost(hash.operands(), HASH_PER_BYTE_COST, HASH_BASE_COST)
+            cost_in_size(stack, finalize, hash.operands(), HASH_PER_BYTE_COST, HASH_BASE_COST)
         }
         Command::Instruction(Instruction::HashManyPSD2(_)) => {
             bail!("`hash_many.psd2` is not supported in finalize.")
@@ -270,6 +310,8 @@ pub fn cost_in_microcredits<N: Network>(stack: &Stack<N>, function_name: &Identi
             let operands = mul.operands();
             ensure!(operands.len() == 2, "mul opcode must have exactly two operands.");
 
+            // Retrieve the finalize types.
+            let finalize_types = stack.get_finalize_types(finalize.name())?;
             // Get the price by operand type.
             let operand_type = finalize_types.get_type_from_operand(stack, &operands[0])?;
             match operand_type {
@@ -291,6 +333,8 @@ pub fn cost_in_microcredits<N: Network>(stack: &Stack<N>, function_name: &Identi
             let operands = pow.operands();
             ensure!(!operands.is_empty(), "pow opcode must have at least one operand.");
 
+            // Retrieve the finalize types.
+            let finalize_types = stack.get_finalize_types(finalize.name())?;
             // Get the price by operand type.
             let operand_type = finalize_types.get_type_from_operand(stack, &operands[0])?;
             match operand_type {
@@ -316,21 +360,20 @@ pub fn cost_in_microcredits<N: Network>(stack: &Stack<N>, function_name: &Identi
         Command::Instruction(Instruction::Ternary(_)) => Ok(500),
         Command::Instruction(Instruction::Xor(_)) => Ok(500),
         Command::Await(_) => Ok(500),
-        Command::Contains(contains) => Ok(operand_size_in_bytes(contains.key())?
-            .saturating_mul(GET_COMMAND_PER_BYTE_COST)
-            .saturating_add(GET_COMMAND_BASE_COST)),
-        Command::Get(get) => Ok(operand_size_in_bytes(get.key())?
-            .saturating_mul(GET_COMMAND_PER_BYTE_COST)
-            .saturating_add(GET_COMMAND_BASE_COST)),
-        Command::GetOrUse(get) => Ok(operand_size_in_bytes(get.key())?
-            .saturating_mul(GET_COMMAND_PER_BYTE_COST)
-            .saturating_add(GET_COMMAND_BASE_COST)),
+        Command::Contains(command) => {
+            cost_in_size(stack, finalize, [command.key()], MAPPING_PER_BYTE_COST, MAPPING_BASE_COST)
+        }
+        Command::Get(command) => {
+            cost_in_size(stack, finalize, [command.key()], MAPPING_PER_BYTE_COST, MAPPING_BASE_COST)
+        }
+        Command::GetOrUse(command) => {
+            cost_in_size(stack, finalize, [command.key()], MAPPING_PER_BYTE_COST, MAPPING_BASE_COST)
+        }
         Command::RandChaCha(_) => Ok(25_000),
-        Command::Remove(_) => Ok(GET_COMMAND_BASE_COST),
-        Command::Set(set) => Ok(operand_size_in_bytes(set.key())?
-            .saturating_add(operand_size_in_bytes(set.value())?)
-            .saturating_mul(SET_COMMAND_PER_BYTE_COST)
-            .saturating_add(SET_COMMAND_BASE_COST)),
+        Command::Remove(_) => Ok(MAPPING_BASE_COST),
+        Command::Set(command) => {
+            cost_in_size(stack, finalize, [command.key(), command.value()], SET_PER_BYTE_COST, SET_BASE_COST)
+        }
         Command::BranchEq(_) | Command::BranchNeq(_) => Ok(500),
         Command::Position(_) => Ok(100),
     };
@@ -342,34 +385,3 @@ pub fn cost_in_microcredits<N: Network>(stack: &Stack<N>, function_name: &Identi
         .map(cost)
         .try_fold(0u64, |acc, res| res.and_then(|x| acc.checked_add(x).ok_or(anyhow!("Finalize cost overflowed"))))
 }
-
-// Helper function to get the plaintext type in bytes.
-fn plaintext_size_in_bytes<N: Network>(stack: &Stack<N>, plaintext_type: &PlaintextType<N>) -> Result<u64> {
-    match plaintext_type {
-        PlaintextType::Literal(literal_type) => Ok(literal_type.size_in_bytes::<N>() as u64),
-        PlaintextType::Struct(struct_identifier) => {
-            // Retrieve the struct from the stack.
-            let plaintext_struct = stack.program().get_struct(struct_identifier)?;
-
-            // Retrieve the size of the struct identifier.
-            let identifier_size = plaintext_struct.name().to_bytes_le()?.len() as u64;
-
-            // Retrieve the size of all the members of the struct.
-            let size_of_members = plaintext_struct
-                .members()
-                .iter()
-                .map(|(_, member_type)| plaintext_size_in_bytes(stack, member_type))
-                .sum::<Result<u64>>()?;
-
-            // Return the size of the struct.
-            Ok(identifier_size.saturating_add(size_of_members))
-        }
-        PlaintextType::Array(array_type) => {
-            // Retrieve the number of elements in the array.
-            let num_array_elements = **array_type.length() as u64;
-
-            // Retrieve the size of the internal array types.
-            Ok(num_array_elements.saturating_mul(plaintext_size_in_bytes(stack, array_type.next_element_type())?))
-        }
-    }
-}
```
