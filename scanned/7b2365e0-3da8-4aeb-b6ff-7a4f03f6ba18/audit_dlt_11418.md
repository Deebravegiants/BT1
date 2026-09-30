# [?] fix: logrows reset after graph creation can cause extended K overflow (#745)

## Summary
Severity: Unknown
Chain: ZK
Component: zkonduit/ezkl
Published: 2024-03-20
Source: https://github.com/zkonduit/ezkl/commit/2ccf05666104a3e238877f5531d7984c61520341
Type: security-commit

## Details
fix: logrows reset after graph creation can cause extended K overflow (#745)

## Patch
### README.md
```diff
@@ -31,9 +31,9 @@ EZKL
 
 [![Notebook](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zkonduit/ezkl/blob/main/examples/notebooks/simple_demo_all_public.ipynb) 
 
-In the backend we use [Halo2](https://github.com/privacy-scaling-explorations/halo2) as a proof system.
+In the backend we use the collaboratively-developed [Halo2](https://github.com/privacy-scaling-explorations/halo2) as a proof system.
 
-The generated proofs can then be used on-chain to verify computation, only the Ethereum Virtual Machine (EVM) is supported at the moment.
+The generated proofs can then be verified with much less computational resources, including on-chain (with the Ethereum Virtual Machine), in a browser, or on a device. 
 
 - If you have any questions, we'd love for you to open up a discussion topic in [Discussions](https://github.com/zkonduit/ezkl/discussions). Alternatively, you can join the ✨[EZKL Community Telegram Group](https://t.me/+QRzaRvTPIthlYWMx)💫.
 
@@ -45,6 +45,8 @@ The generated proofs can then be used on-chain to verify computation, only the E
 
 ### getting started ⚙️
 
+The easiest way to get started is to try out a notebook. 
+
 #### Python
 Install the python bindings by calling.
 
@@ -70,7 +72,7 @@ curl https://raw.githubusercontent.com/zkonduit/ezkl/main/install_ezkl_cli.sh |
 
 https://user-images.githubusercontent.com/45801863/236771676-5bbbbfd1-ba6f-418a-902e-20738ce0e9f0.mp4
 
-For more details visit the [docs](https://docs.ezkl.xyz).
+For more details visit the [docs](https://docs.ezkl.xyz). The CLI is faster than Python, as it has less overhead. For even more speed and convenience, check out the [remote proving service](https://ei40vx5x6j0.typeform.com/to/sFv1oxvb), which feels like the CLI but is backed by a tuned cluster.
 
 Build the auto-generated rust documentation and open the docs in your browser locally. `cargo doc --open`
 
@@ -124,17 +126,6 @@ unset ENABLE_ICICLE_GPU
 
 **NOTE:** Even with the above environment variable set, icicle is disabled for circuits where k <= 8. To change the value of `k` where icicle is enabled, you can set the environment variable `ICICLE_SMALL_K`.
 
-### repos
-
-The EZKL project has several libraries and repos. 
-
-| Repo | Description |
-| --- | --- |
-| [@zkonduit/ezkl](https://github.com/zkonduit/ezkl) | the main ezkl repo in rust with wasm and python bindings |
-| [@zkonduit/ezkljs](https://github.com/zkonduit/ezkljs) | typescript and javascript tooling to help integrate ezkl into web apps |
-
-----------------------
-
 ### contributing 🌎
 
 If you're interested in contributing and are unsure where to start, reach out to one of the maintainers:
@@ -151,12 +142,15 @@ More broadly:
 - To report bugs or request new features [create a new issue within Issues](https://github.com/zkonduit/ezkl/issues) to inform the greater community.
 
 
-Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in the work by you shall be licensed to Zkonduit Inc. under the terms and conditions specified in the [CLA](https://github.com/zkonduit/ezkl/blob/main/cla.md), which you agree to by intentionally submitting a contribution. In particular, you have the right to submit the contribution and we can distribute it under the Apache 2.0 license, among other terms and conditions. 
+Any contribution intentionally submitted for inclusion in the work by you shall be licensed to Zkonduit Inc. under the terms and conditions specified in the [CLA](https://github.com/zkonduit/ezkl/blob/main/cla.md), which you agree to by intentionally submitting a contribution. In particular, you have the right to submit the contribution and we can distribute it, among other terms and conditions. 
 
 ### no security guarantees
 
 Ezkl is unaudited, beta software undergoing rapid development. There may be bugs. No guarantees of security are made and it should not be relied on in production.
 
 > NOTE: Because operations are quantized when they are converted from an onnx file to a zk-circuit, outputs in python and ezkl may differ slightly. 
 
+### no warranty
 
+Copyright (c) 2024 Zkonduit Inc. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
+FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```

### src/circuit/table.rs
```diff
@@ -6,7 +6,7 @@ use halo2_proofs::{
     circuit::{Layouter, Value},
     plonk::{ConstraintSystem, Expression, TableColumn},
 };
-use log::warn;
+use log::{debug, warn};
 use maybe_rayon::prelude::{IntoParallelIterator, ParallelIterator};
 
 use crate::{
@@ -165,7 +165,7 @@ impl<F: PrimeField + TensorType + PartialOrd> Table<F> {
         let num_cols = table_inputs.len();
 
         if num_cols > 1 {
-            warn!("Using {} columns for non-linearity table.", num_cols);
+            debug!("Using {} columns for non-linearity table.", num_cols);
         }
 
         let table_outputs = table_inputs
```

### src/graph/mod.rs
```diff
@@ -1171,17 +1171,6 @@ impl GraphCircuit {
             .settings()
             .clone();
 
-        // recalculate the logrows if there has been overflow on the constants
-        settings_mut.run_args.logrows = std::cmp::max(
-            settings_mut.run_args.logrows,
-            settings_mut.constants_logrows(),
-        );
-        // recalculate the logrows if there has been overflow for the model constraints
-        settings_mut.run_args.logrows = std::cmp::max(
-            settings_mut.run_args.logrows,
-            settings_mut.model_constraint_logrows(),
-        );
-
         debug!(
             "setting lookup_range to: {:?}, setting logrows to: {}",
             self.settings().run_args.lookup_range,
```

### src/tensor/var.rs
```diff
@@ -1,6 +1,6 @@
 use std::collections::HashSet;
 
-use log::{error, warn};
+use log::{debug, error, warn};
 
 use crate::circuit::CheckMode;
 
@@ -104,7 +104,7 @@ impl VarTensor {
         let mut advices = vec![];
 
         if modulo > 1 {
-            warn!("using column duplication for {} advice blocks", modulo - 1);
+            debug!("using column duplication for {} advice blocks", modulo - 1);
         }
 
         for _ in 0..modulo {
@@ -150,7 +150,7 @@ impl VarTensor {
         modulo = (num_constants + modulo) / max_rows + 1;
 
         if modulo > 1 {
-            warn!("using column duplication for {} fixed columns", modulo - 1);
+            debug!("using column duplication for {} fixed columns", modulo - 1);
         }
 
         for _ in 0..modulo {
```
