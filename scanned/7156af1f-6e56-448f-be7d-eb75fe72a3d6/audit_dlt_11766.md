# [?] Fix terminology, fix vulnerability

## Summary
Severity: Unknown
Chain: Aleo
Component: AleoNet/snarkVM-test
Published: 2024-01-21
Source: https://github.com/AleoNet/snarkVM-test/commit/722b6d0623125d41feb40cdb73ebe7bffa837b24
Type: security-commit

## Details
Fix terminology, fix vulnerability

## Patch
### circuit/environment/src/circuit.rs
```diff
@@ -22,9 +22,9 @@ use core::{
 type Field = <console::Testnet3 as console::Environment>::Field;
 
 thread_local! {
+    pub(super) static CONSTRAINT_LIMIT: Cell<Option<u64>> = Cell::new(None);
     pub(super) static CIRCUIT: RefCell<R1CS<Field>> = RefCell::new(R1CS::new());
     pub(super) static IN_WITNESS: Cell<bool> = Cell::new(false);
-    pub(super) static MAX_NUM_CONSTRAINTS: Cell<u64> = Cell::new(u64::MAX);
     pub(super) static ZERO: LinearCombination<Field> = LinearCombination::zero();
     pub(super) static ONE: LinearCombination<Field> = LinearCombination::one();
 }
@@ -147,10 +147,12 @@ impl Environment for Circuit {
             // Ensure we are not in witness mode.
             if !in_witness.get() {
                 CIRCUIT.with(|circuit| {
-                    // Ensure we do not surpass maximum allowed number of constraints
-                    MAX_NUM_CONSTRAINTS.with(|max_constraints| {
-                        if circuit.borrow().num_constraints() >= max_constraints.get() {
-                            Self::halt("Surpassing maximum allowed number of constraints")
+                    // Ensure that we do not surpass the constraint limit for the circuit.
+                    CONSTRAINT_LIMIT.with(|constraint_limit| {
+                        if let Some(limit) = constraint_limit.get() {
+                            if circuit.borrow().num_constraints() >= limit {
+                                Self::halt(format!("Surpassed the constraint limit ({limit})"))
+                            }
                         }
                     });
 
@@ -256,8 +258,11 @@ impl Environment for Circuit {
         panic!("{}", &error)
     }
 
-    /// TODO (howardwu): Abstraction - Refactor this into an appropriate design.
-    ///  Circuits should not have easy access to this during synthesis.
+    /// Sets the constraint limit for the circuit.
+    fn set_constraint_limit(limit: Option<u64>) {
+        CONSTRAINT_LIMIT.with(|current_limit| current_limit.replace(limit));
+    }
+
     /// Returns the R1CS circuit, resetting the circuit.
     fn inject_r1cs(r1cs: R1CS<Self::BaseField>) {
         CIRCUIT.with(|circuit| {
@@ -276,15 +281,13 @@ impl Environment for Circuit {
         })
     }
 
-    /// TODO (howardwu): Abstraction - Refactor this into an appropriate design.
-    ///  Circuits should not have easy access to this during synthesis.
     /// Returns the R1CS circuit, resetting the circuit.
     fn eject_r1cs_and_reset() -> R1CS<Self::BaseField> {
         CIRCUIT.with(|circuit| {
             // Reset the witness mode.
             IN_WITNESS.with(|in_witness| in_witness.replace(false));
-            // Reset the max num constraints.
-            Self::set_constraint_maximum(u64::MAX);
+            // Reset the constraint limit.
+            Self::set_constraint_limit(None);
             // Eject the R1CS instance.
             let r1cs = circuit.replace(R1CS::<<Self as Environment>::BaseField>::new());
             // Ensure the circuit is now empty.
@@ -297,15 +300,13 @@ impl Environment for Circuit {
         })
     }
 
-    /// TODO (howardwu): Abstraction - Refactor this into an appropriate design.
-    ///  Circuits should not have easy access to this during synthesis.
     /// Returns the R1CS assignment of the circuit, resetting the circuit.
     fn eject_assignment_and_reset() -> Assignment<<Self::Network as console::Environment>::Field> {
         CIRCUIT.with(|circuit| {
             // Reset the witness mode.
             IN_WITNESS.with(|in_witness| in_witness.replace(false));
-            // Reset the num constraints.
-            Self::set_constraint_maximum(u64::MAX);
+            // Reset the constraint limit.
+            Self::set_constraint_limit(None);
             // Eject the R1CS instance.
             let r1cs = circuit.replace(R1CS::<<Self as Environment>::BaseField>::new());
             assert_eq!(0, circuit.borrow().num_constants());
@@ -317,18 +318,14 @@ impl Environment for Circuit {
         })
     }
 
-    /// Sets a maximum number of allowed constraints.
-    fn set_constraint_maximum(new_max_num_constraints: u64) {
-        MAX_NUM_CONSTRAINTS.with(|max_num_constraints| max_num_constraints.replace(new_max_num_constraints));
-    }
-
     /// Clears the circuit and initializes an empty environment.
     fn reset() {
         CIRCUIT.with(|circuit| {
             // Reset the witness mode.
             IN_WITNESS.with(|in_witness| in_witness.replace(false));
-            // Reset the max num constraints.
-            Self::set_constraint_maximum(u64::MAX);
+            // Reset the constraint limit.
+            Self::set_constraint_limit(None);
+            // Reset the circuit.
             *circuit.borrow_mut() = R1CS::<<Self as Environment>::BaseField>::new();
             assert_eq!(0, circuit.borrow().num_constants());
             assert_eq!(1, circuit.borrow().num_public());
```

### circuit/environment/src/environment.rs
```diff
@@ -160,6 +160,9 @@ pub trait Environment: 'static + Copy + Clone + fmt::Debug + fmt::Display + Eq +
         <Self::Network as console::Environment>::halt(message)
     }
 
+    /// Sets the constraint limit for the circuit.
+    fn set_constraint_limit(limit: Option<u64>);
+
     /// Returns the R1CS circuit, resetting the circuit.
     fn inject_r1cs(r1cs: R1CS<Self::BaseField>);
 
@@ -169,9 +172,6 @@ pub trait Environment: 'static + Copy + Clone + fmt::Debug + fmt::Display + Eq +
     /// Returns the R1CS assignment of the circuit, resetting the circuit.
     fn eject_assignment_and_reset() -> Assignment<<Self::Network as console::Environment>::Field>;
 
-    /// Sets a maximum amount of allowed constraints
-    fn set_constraint_maximum(new_max_num_constraints: u64);
-
     /// Clears and initializes an empty environment.
     fn reset();
 }
```

### circuit/network/src/v0.rs
```diff
@@ -466,6 +466,11 @@ impl Environment for AleoV0 {
         E::halt(message)
     }
 
+    /// Sets the constraint limit for the circuit.
+    fn set_constraint_limit(limit: Option<u64>) {
+        E::set_constraint_limit(limit)
+    }
+
     /// Returns the R1CS circuit, resetting the circuit.
     fn inject_r1cs(r1cs: R1CS<Self::BaseField>) {
         E::inject_r1cs(r1cs)
@@ -481,11 +486,6 @@ impl Environment for AleoV0 {
         E::eject_assignment_and_reset()
     }
 
-    /// Sets a maximum amount of allowed constraints
-    fn set_constraint_maximum(new_max_num_constraints: u64) {
-        E::set_constraint_maximum(new_max_num_constraints)
-    }
-
     /// Clears the circuit and initializes an empty environment.
     fn reset() {
         E::reset()
```

### ledger/block/src/transaction/deployment/mod.rs
```diff
@@ -124,9 +124,21 @@ impl<N: Network> Deployment<N> {
         &self.verifying_keys
     }
 
-    /// Returns the total number of constraints.
-    pub fn num_constraints(&self) -> u64 {
-        self.verifying_keys.iter().map(|(_, (vk, _))| vk.circuit_info.num_constraints as u64).sum::<u64>()
+    /// Returns the sum of the constraint counts for all functions in this deployment.
+    pub fn num_combined_constraints(&self) -> Result<u64> {
+        // Initialize the accumulator.
+        let mut num_combined_constraints = 0u64;
+        // Iterate over the functions.
+        for (_, (vk, _)) in &self.verifying_keys {
+            // Add the number of constraints.
+            // Note: This method must be *checked* because the claimed constraint count
+            // is from the user, not the synthesizer.
+            num_combined_constraints = num_combined_constraints
+                .checked_add(vk.circuit_info.num_constraints as u64)
+                .ok_or_else(|| anyhow!("Overflow when counting constraints for '{}'", self.program_id()))?;
+        }
+        // Return the number of combined constraints.
+        Ok(num_combined_constraints)
     }
 
     /// Returns the deployment ID.
```

### synthesizer/process/src/stack/call/mod.rs
```diff
@@ -353,7 +353,7 @@ impl<N: Network> CallTrait<N> for Call<N> {
 
             // If the circuit is in CheckDeployment mode, set a constraint maximum.
             if let CallStack::CheckDeployment(_, _, _, num_constraints) = &registers.call_stack() {
-                A::set_constraint_maximum(*num_constraints);
+                A::set_constraint_limit(Some(*num_constraints));
             }
 
             use circuit::Inject;
```

### synthesizer/process/src/stack/deploy.rs
```diff
@@ -74,7 +74,7 @@ impl<N: Network> Stack<N> {
         let program_id = self.program.id();
 
         // Check that the deployment does not require too many constraints
-        let total_num_constraints = deployment.num_constraints();
+        let total_num_constraints = deployment.num_combined_constraints()?;
         ensure!(total_num_constraints <= N::MAX_DEPLOYMENT_CONSTRAINTS);
 
         // Construct the call stacks and assignments used to verify the certificates.
```

### synthesizer/process/src/stack/execute.rs
```diff
@@ -144,7 +144,7 @@ impl<N: Network> StackExecute<N> for Stack<N> {
 
         // If the circuit is in CheckDeployment mode, set a constraint maximum.
         if let CallStack::CheckDeployment(_, _, _, num_constraints) = &call_stack {
-            A::set_constraint_maximum(*num_constraints);
+            A::set_constraint_limit(Some(*num_constraints));
         }
 
         // Retrieve the next request.
```

### synthesizer/src/vm/helpers/cost.rs
```diff
@@ -32,7 +32,7 @@ pub fn deployment_cost<N: Network>(deployment: &Deployment<N>) -> Result<u64> {
     // Determine the number of characters in the program ID.
     let num_characters = u32::try_from(program_id.name().to_string().len())?;
     // Determine the number of constraints in the program
-    let num_constraints = deployment.num_constraints();
+    let num_constraints = deployment.num_combined_constraints()?;
 
     // Compute the storage cost in microcredits.
     let storage_cost = size_in_bytes
```
