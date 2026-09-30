# [?] fix: non determinism when creating constraints (#55)

## Summary
Severity: Unknown
Chain: ZK
Component: zkonduit/ezkl
Published: 2022-11-01
Source: https://github.com/zkonduit/ezkl/commit/159e91a58d3c95efbedd60ad733e7c75b84bd87d
Type: security-commit

## Details
fix: non determinism when creating constraints (#55)

* hashmap swapped for btreemap

* fix and add integration tests for full proofs and prove and verify (small examples)

Co-authored-by: jason <jason.morton@gmail.com>

## Patch
### examples/onnx_models/relu.onnx
```diff
@@ -0,0 +1,13 @@
+pytorch1.12.1:q
+

+inputoutputRelu_0"Relu	torch_jitZ!
+input
+
+

+batch_size
+b"
+output
+
+

+batch_size
+B
```

### examples/onnx_models/relu_input.json
```diff
@@ -0,0 +1 @@
+{"input_shapes": [[3]], "input_data": [[-0.40077725052833557, 2.493845224380493, 0.5796360969543457]], "public_inputs": [[0.0, 2.493845224380493, 0.5796360969543457]]}
\ No newline at end of file
```

### examples/onnx_models/relurelu_small.onnx
```diff
@@ -0,0 +1,15 @@
+pytorch1.12.1:�
+

+inputinput.1Relu_0"Relu
+
+input.1outputRelu_1"Relu	torch_jitZ!
+input
+
+

+batch_size
+b"
+output
+
+

+batch_size
+B
```

### examples/onnx_models/relurelu_small_input.json
```diff
@@ -0,0 +1 @@
+{"input_shapes": [[3]], "input_data": [[3.394426107406616, 1.1624923944473267, -0.5661267638206482]], "public_inputs": [[3.394426107406616, 1.1624923944473267, 0.0]]}
\ No newline at end of file
```

### examples/onnx_models/relusig_small.onnx
```diff
@@ -0,0 +1,15 @@
+pytorch1.12.1:�
+&
+inputonnx::Sigmoid_3Relu_0"Relu
+-
+onnx::Sigmoid_3output	Sigmoid_1"Sigmoid	torch_jitZ!
+input
+
+

+batch_size
+b"
+output
+
+

+batch_size
+B
```

### examples/onnx_models/relusig_small_input.json
```diff
@@ -0,0 +1 @@
+{"input_shapes": [[3]], "input_data": [[-0.3827013373374939, 1.3510069847106934, -0.08920183777809143]], "public_inputs": [[0.5, 0.7942942380905151, 0.5]]}
\ No newline at end of file
```

### examples/onnx_models/sig.onnx
```diff
@@ -0,0 +1,13 @@
+pytorch1.12.1:w
+#
+inputoutput	Sigmoid_0"Sigmoid	torch_jitZ!
+input
+
+

+batch_size
+b"
+output
+
+

+batch_size
+B
```

### examples/onnx_models/sig_input.json
```diff
@@ -0,0 +1 @@
+{"input_shapes": [[3]], "input_data": [[-0.008400974795222282, 0.18489880859851837, -0.7444106340408325]], "public_inputs": [[0.4978998005390167, 0.5460934638977051, 0.3220404088497162]]}
\ No newline at end of file
```

### src/circuit/fused.rs
```diff
@@ -13,7 +13,7 @@ use std::fmt;
 use std::marker::PhantomData;
 
 /// An enum representing the operations that can be merged into a single circuit gate.
-#[derive(Clone, Debug, PartialEq, Eq, Hash)]
+#[derive(Clone, Debug, PartialEq, Eq, Hash, PartialOrd, Ord)]
 pub enum FusedOp {
     Add,
     Sub,
```

### src/onnx/model.rs
```diff
@@ -15,7 +15,7 @@ use halo2_proofs::{
 use itertools::Itertools;
 use log::{debug, error, info, trace, warn};
 use std::cmp::max;
-use std::collections::{hash_map::Entry, HashMap, HashSet};
+use std::collections::{btree_map::Entry, BTreeMap, HashSet};
 use std::fmt;
 use std::path::Path;
 use tabled::{Table, Tabled};
@@ -95,7 +95,7 @@ pub struct NodeConfig<F: FieldExt + TensorType> {
 /// A circuit configuration for the entirety of a model loaded from an Onnx file.
 #[derive(Clone)]
 pub struct OnnxModelConfig<F: FieldExt + TensorType> {
-    configs: HashMap<usize, NodeConfig<F>>,
+    configs: BTreeMap<usize, NodeConfig<F>>,
     pub model: OnnxModel,
     pub public_outputs: Vec<Column<Instance>>,
 }
@@ -327,17 +327,17 @@ impl OnnxNode {
 
 /// Representation of an execution graph divided into execution 'buckets'.
 #[derive(Clone, Default, Debug)]
-pub struct NodeGraph(HashMap<Option<usize>, HashMap<usize, OnnxNode>>);
+pub struct NodeGraph(BTreeMap<Option<usize>, BTreeMap<usize, OnnxNode>>);
 
 impl NodeGraph {
     pub fn new() -> Self {
-        NodeGraph(HashMap::new())
+        NodeGraph(BTreeMap::new())
     }
 
     fn insert(&mut self, idx: Option<usize>, node_idx: usize, config: OnnxNode) {
         match self.0.entry(idx) {
             Entry::Vacant(e) => {
-                e.insert(HashMap::from([(node_idx, config)]));
+                e.insert(BTreeMap::from([(node_idx, config)]));
             }
             Entry::Occupied(mut e) => {
                 e.get_mut().insert(node_idx, config);
@@ -406,14 +406,14 @@ impl OnnxModel {
     pub fn new(path: impl AsRef<Path>, scale: i32, bits: usize, mode: Mode) -> Self {
         let model = tract_onnx::onnx().model_for_path(path).unwrap();
 
-        let onnx_nodes: HashMap<usize, OnnxNode> = model
+        let onnx_nodes: BTreeMap<usize, OnnxNode> = model
             .nodes()
             .iter()
             .enumerate()
             .map(|(i, n)| (i, OnnxNode::new(n.clone(), scale, i)))
             .collect();
 
-        let mut map = HashMap::new();
+        let mut map = BTreeMap::new();
         map.insert(None, onnx_nodes);
         let mut om = OnnxModel {
             model,
@@ -472,10 +472,10 @@ impl OnnxModel {
         advices: VarTensor,
     ) -> Result<OnnxModelConfig<F>> {
         info!("configuring model");
-        let mut results = HashMap::new();
+        let mut results = BTreeMap::new();
 
         for (_, bucket_nodes) in self.onnx_nodes.0.iter() {
-            let non_fused_ops: HashMap<&usize, &OnnxNode> = bucket_nodes
+            let non_fused_ops: BTreeMap<&usize, &OnnxNode> = bucket_nodes
                 .iter()
                 .filter(|(_, n)| !n.opkind.is_fused())
                 .collect();
@@ -493,7 +493,7 @@ impl OnnxModel {
             }
 
             // preserves ordering
-            let fused_ops: HashMap<&usize, &OnnxNode> = bucket_nodes
+            let fused_ops: BTreeMap<&usize, &OnnxNode> = bucket_nodes
                 .iter()
                 .filter(|(_, n)| n.opkind.is_fused())
                 .collect();
@@ -527,21 +527,21 @@ impl OnnxModel {
         })
     }
 
-    /// Configures a `HashMap` of 'fuseable' operations. These correspond to operations that are represented in
+    /// Configures a `BTreeMap` of 'fuseable' operations. These correspond to operations that are represented in
     /// the `circuit::fused` module. A single configuration is output, representing the amalgamation of these operations into
     /// a single Halo2 gate.
     /// # Arguments
     ///
-    /// * `nodes` - A `HashMap` of (node index, [OnnxNode] pairs). The [OnnxNode] must represent a fuseable op.
+    /// * `nodes` - A `BTreeMap` of (node index, [OnnxNode] pairs). The [OnnxNode] must represent a fuseable op.
     /// * `meta` - Halo2 ConstraintSystem.
     /// * `advices` - A `VarTensor` holding columns of advices. Must be sufficiently large to configure all the passed `nodes`.
     fn fuse_ops<F: FieldExt + TensorType>(
         &self,
-        nodes: &HashMap<&usize, &OnnxNode>,
+        nodes: &BTreeMap<&usize, &OnnxNode>,
         meta: &mut ConstraintSystem<F>,
         advices: VarTensor,
     ) -> NodeConfigTypes<F> {
-        let input_nodes: HashMap<(&usize, &FusedOp), Vec<OnnxNode>> = nodes
+        let input_nodes: BTreeMap<(&usize, &FusedOp), Vec<OnnxNode>> = nodes
             .iter()
             .map(|(i, e)| {
                 (
@@ -568,7 +568,6 @@ impl OnnxModel {
         // impose an execution order here
         let inputs_to_layer: Vec<(usize, VarTensor)> = input_nodes
             .iter()
-            .sorted_by_key(|x| x.0 .0)
             .flat_map(|x| {
                 x.1.iter()
                     .filter(|i| !nodes.contains_key(&i.idx) && seen.insert(i.idx))
@@ -602,7 +601,6 @@ impl OnnxModel {
         let mut inter_counter = 0;
         let fused_nodes: Vec<FusedNode> = input_nodes
             .iter()
-            .sorted_by_key(|x| x.0 .0)
             .map(|(op, e)| {
                 let order = e
                     .iter()
@@ -745,11 +743,11 @@ impl OnnxModel {
         inputs: &[ValTensor<F>],
     ) -> Result<Vec<ValTensor<F>>> {
         info!("model layout");
-        let mut results = HashMap::<usize, ValTensor<F>>::new();
+        let mut results = BTreeMap::<usize, ValTensor<F>>::new();
         for i in inputs.iter().enumerate() {
             results.insert(i.0, i.1.clone());
         }
-        for (idx, c) in config.configs.iter().sorted_by_key(|x| x.0) {
+        for (idx, c) in config.configs.iter() {
             let mut display: String = "".to_string();
             for (i, idx) in c.onnx_idx[0..].iter().enumerate() {
                 let node = &self.onnx_nodes.filter(*idx);
@@ -797,11 +795,11 @@ impl OnnxModel {
     ///
     /// * `config` - [NodeConfig] the signle region we will layout.
     /// * `layouter` - Halo2 Layouter.
-    /// * `inputs` - `HashMap` of values to feed into the NodeConfig, can also include previous intermediate results, i.e the output of other nodes.
+    /// * `inputs` - `BTreeMap` of values to feed into the NodeConfig, can also include previous intermediate results, i.e the output of other nodes.
     fn layout_config<F: FieldExt + TensorType>(
         &self,
         layouter: &mut impl Layouter<F>,
-        inputs: &mut HashMap<usize, ValTensor<F>>,
+        inputs: &mut BTreeMap<usize, ValTensor<F>>,
         config: &NodeConfig<F>,
     ) -> Result<Option<ValTensor<F>>> {
         // The node kind and the config should be the same.
@@ -854,17 +852,10 @@ impl OnnxModel {
     pub fn forward_shape_and_quantize_pass(&mut self) -> Result<()> {
         info!("quantizing model activations");
 
-        let mut nodes = HashMap::<usize, OnnxNode>::new();
+        let mut nodes = BTreeMap::<usize, OnnxNode>::new();
         let output_nodes = self.model.outputs.iter().map(|o| o.node).collect_vec();
 
-        for (_, node) in self
-            .onnx_nodes
-            .0
-            .get_mut(&None)
-            .unwrap()
-            .iter_mut()
-            .sorted_by_key(|x| x.0)
-        {
+        for (_, node) in self.onnx_nodes.0.get_mut(&None).unwrap().iter_mut() {
             if output_nodes.contains(&node.idx) {
                 node.is_output = true;
             }
@@ -1207,17 +1198,17 @@ impl OnnxModel {
     /// If the node is a lookup table, assign to it the maximum bucket of it's inputs incremented by 1.
     /// # Arguments
     ///
-    /// * `nodes` - `HashMap` of (node index, [OnnxNode]) pairs.
+    /// * `nodes` - `BTreeMap` of (node index, [OnnxNode]) pairs.
     pub fn assign_execution_buckets(
         &mut self,
-        mut nodes: HashMap<usize, OnnxNode>,
+        mut nodes: BTreeMap<usize, OnnxNode>,
     ) -> Result<NodeGraph> {
         info!("assigning configuration buckets to operations");
 
         let mut bucketed_nodes =
-            NodeGraph(HashMap::<Option<usize>, HashMap<usize, OnnxNode>>::new());
+            NodeGraph(BTreeMap::<Option<usize>, BTreeMap<usize, OnnxNode>>::new());
 
-        for (_, node) in nodes.iter_mut().sorted_by_key(|x| x.0) {
+        for (_, node) in nodes.iter_mut() {
             let prev_bucket: Option<usize> = node
                 .inputs
                 .iter()
```

### tests/integration_tests.rs
```diff
@@ -1,6 +1,7 @@
 use std::process::Command;
 
-fn test_onnx_example(example_name: String) {
+// Mock prove (fast, but does not cover some potential issues)
+fn test_onnx_mock(example_name: String) {
     let status = Command::new("cargo")
         .args([
             "run",
@@ -26,27 +27,28 @@ fn test_onnx_example(example_name: String) {
 }
 
 #[test]
-fn test_ff_example() {
-    test_onnx_example("ff".to_string());
+fn test_ff_mock() {
+    test_onnx_mock("ff".to_string());
 }
 
 #[test]
-fn test_relusig_example() {
-    test_onnx_example("relusig".to_string());
+fn test_relusig_mock() {
+    test_onnx_mock("relusig".to_string());
 }
 
 #[test]
 #[ignore]
-fn test_1lcnvrl_example() {
-    test_onnx_example("1lcnvrl".to_string());
+fn test_1lcnvrl_mock() {
+    test_onnx_mock("1lcnvrl".to_string());
 }
 
 #[test]
-fn test_2lcnvrl_example() {
-    test_onnx_example("2lcnvrl_relusig".to_string());
+fn test_2lcnvrl_mock() {
+    test_onnx_mock("2lcnvrl_relusig".to_string());
 }
 
-fn test_onnx_prove_and_verify(example_name: String) {
+// full prove (slower, covers more, but still reuses the pk)
+fn test_onnx_fullprove(example_name: String) {
     let status = Command::new("cargo")
         .args([
             "run",
@@ -63,6 +65,98 @@ fn test_onnx_prove_and_verify(example_name: String) {
             format!("./examples/onnx_models/{}_input.json", example_name).as_str(),
             "-M",
             format!("./examples/onnx_models/{}.onnx", example_name).as_str(),
+            // "-K",
+            // "2",  //causes failure
+        ])
+        .status()
+        .expect("failed to execute process");
+    assert!(status.success());
+}
+
+#[test]
+fn test_ff_fullprove() {
+    test_onnx_fullprove("ff".to_string());
+}
+
+#[test]
+#[ignore]
+fn test_relusig_fullprove() {
+    test_onnx_fullprove("relusig".to_string());
+}
+
+#[test]
+fn test_relurelu_fullprove() {
+    test_onnx_fullprove("relurelu_small".to_string());
+}
+
+#[test]
+fn test_relusig_small_fullprove() {
+    test_onnx_fullprove("relusig_small".to_string());
+}
+
+#[test]
+fn test_relu_fullprove() {
+    test_onnx_fullprove("relu".to_string());
+}
+
+#[test]
+fn test_sig_fullprove() {
+    test_onnx_fullprove("sig".to_string());
+}
+
+// These require too much memory for Github CI right now
+#[test]
+#[ignore]
+fn test_1lcnvrl_fullprove() {
+    test_onnx_fullprove("1lcnvrl".to_string());
+}
+
+#[test]
+#[ignore]
+fn test_2lcnvrl_fullprove() {
+    test_onnx_fullprove("2lcnvrl_relusig".to_string());
+}
+
+// prove-serialize-verify, the usual full path
+fn test_onnx_prove_and_verify(example_name: String) {
+    let status = Command::new("cargo")
+        .args([
+            "run",
+            "--release",
+            "--bin",
+            "ezkl",
+            "--",
+            "--bits",
+            "16",
+            "-K",
+            "17",
+            "prove",
+            "-D",
+            format!("./examples/onnx_models/{}_input.json", example_name).as_str(),
+            "-M",
+            format!("./examples/onnx_models/{}.onnx", example_name).as_str(),
+            "-O",
+            format!("pav_{}.pf", example_name).as_str(),
+        ])
+        .status()
+        .expect("failed to execute process");
+    assert!(status.success());
+    let status = Command::new("cargo")
+        .args([
+            "run",
+            "--release",
+            "--bin",
+            "ezkl",
+            "--",
+            "--bits",
+            "16",
+            "-K",
+            "17",
+            "verify",
+            "-M",
+            format!("./examples/onnx_models/{}.onnx", example_name).as_str(),
+            "-P",
+            format!("pav_{}.pf", example_name).as_str(),
         ])
         .status()
         .expect("failed to execute process");
@@ -73,3 +167,23 @@ fn test_onnx_prove_and_verify(example_name: String) {
 fn test_ff_pav() {
     test_onnx_prove_and_verify("ff".to_string());
 }
+
+#[test]
+fn test_relusig_pav() {
+    test_onnx_prove_and_verify("relusig_small".to_string());
+}
+
+#[test]
+fn test_relurelu_pav() {
+    test_onnx_prove_and_verify("relurelu_small".to_string());
+}
+
+#[test]
+fn test_relu_pav() {
+    test_onnx_prove_and_verify("relu".to_string());
+}
+
+#[test]
+fn test_sig_pav() {
+    test_onnx_prove_and_verify("sig".to_string());
+}
```
