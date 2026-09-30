# [?] fix: node parsing should not panic (#912)

## Summary
Severity: Unknown
Chain: ZK
Component: zkonduit/ezkl
Published: 2025-01-22
Source: https://github.com/zkonduit/ezkl/commit/d0ba505baa5fa99af1bafc1da10e0235ffe425ce
Type: security-commit

## Details
fix: node parsing should not panic (#912)

## Patch
### .github/workflows/rust.yml
```diff
@@ -779,6 +779,8 @@ jobs:
         run: python -m venv .env --clear; source .env/bin/activate; pip install -r requirements.txt; python -m ensurepip --upgrade
       - name: Build python ezkl
         run: source .env/bin/activate; unset CONDA_PREFIX; maturin develop --features python-bindings --release
+      - name: Voice tutorial
+        run: source .env/bin/activate; cargo nextest run py_tests::tests::voice_
       - name: Neural bow
         run: source .env/bin/activate; cargo nextest run py_tests::tests::neural_bag_of_words_ --no-capture
       - name: Felt conversion
@@ -798,8 +800,6 @@ jobs:
       #     chmod 600 /home/ubuntu/.kaggle/kaggle.json
       - name: All notebooks
         run: source .env/bin/activate; cargo nextest run py_tests::tests::run_notebook_ --test-threads 1
-      - name: Voice tutorial
-        run: source .env/bin/activate; cargo nextest run py_tests::tests::voice_
       - name: NBEATS tutorial
         run: source .env/bin/activate; cargo nextest run py_tests::tests::nbeats_
       # - name: Reusable verifier tutorial
```

### src/circuit/table.rs
```diff
@@ -132,21 +132,16 @@ impl<F: PrimeField + TensorType + PartialOrd + std::hash::Hash> Table<F> {
         (first_element, op_f.output[0])
     }
 
-    ///
+    /// calculates the column size given the number of rows and reserved blinding rows
     pub fn cal_col_size(logrows: usize, reserved_blinding_rows: usize) -> usize {
         2usize.pow(logrows as u32) - reserved_blinding_rows
     }
-
-    ///
-    pub fn cal_bit_range(bits: usize, reserved_blinding_rows: usize) -> usize {
-        2usize.pow(bits as u32) - reserved_blinding_rows
-    }
 }
 
 ///
 pub fn num_cols_required(range_len: IntegerRep, col_size: usize) -> usize {
     // number of cols needed to store the range
-    (range_len / (col_size as IntegerRep)) as usize + 1
+    (range_len / col_size as IntegerRep) as usize + 1
 }
 
 impl<F: PrimeField + TensorType + PartialOrd + std::hash::Hash> Table<F> {
@@ -355,16 +350,11 @@ impl<F: PrimeField + TensorType + PartialOrd + std::hash::Hash> RangeCheck<F> {
         integer_rep_to_felt(chunk * (self.col_size as IntegerRep) + self.range.0)
     }
 
-    ///
+    /// calculates the column size
     pub fn cal_col_size(logrows: usize, reserved_blinding_rows: usize) -> usize {
         2usize.pow(logrows as u32) - reserved_blinding_rows
     }
 
-    ///
-    pub fn cal_bit_range(bits: usize, reserved_blinding_rows: usize) -> usize {
-        2usize.pow(bits as u32) - reserved_blinding_rows
-    }
-
     /// get column index given input
     pub fn get_col_index(&self, input: F) -> F {
         //    range is split up into chunks of size col_size, find the chunk that input is in
```

### src/graph/errors.rs
```diff
@@ -11,6 +11,12 @@ pub enum GraphError {
     /// Shape mismatch in circuit construction
     #[error("invalid dimensions used for node {0} ({1})")]
     InvalidDims(usize, String),
+    /// Non scalar power
+    #[error("we only support scalar powers")]
+    NonScalarPower,
+    /// Non scalar base for exponentiation
+    #[error("we only support scalar bases for exponentiation")]
+    NonScalarBase,
     /// Wrong method was called to configure an op
     #[error("wrong method was called to configure node {0} ({1})")]
     WrongMethod(usize, String),
@@ -143,4 +149,7 @@ pub enum GraphError {
     /// Invalid RunArg
     #[error("invalid RunArgs: {0}")]
     InvalidRunArgs(String),
+    /// Only nearest neighbor interpolation is supported
+    #[error("only nearest neighbor interpolation is supported")]
+    InvalidInterpolation,
 }
```

### src/graph/utilities.rs
```diff
@@ -44,11 +44,10 @@ use tract_onnx::tract_hir::{
     tract_core::ops::cnn::{conv::KernelFormat, MaxPool, SumPool},
 };
 
-/// Quantizes an iterable of f32s to a [Tensor] of i32s using a fixed point representation.
+/// Quantizes an iterable of f64 to a [Tensor] of IntegerRep using a fixed point representation.
 /// Arguments
 ///
-/// * `vec` - the vector to quantize.
-/// * `dims` - the dimensionality of the resulting [Tensor].
+/// * `elem` - the element to quantize.
 /// * `shift` - offset used in the fixed point representation.
 /// * `scale` - `2^scale` used in the fixed point representation.
 pub fn quantize_float(
@@ -85,7 +84,7 @@ pub fn scale_to_multiplier(scale: crate::Scale) -> f64 {
     f64::powf(2., scale as f64)
 }
 
-/// Converts a scale (log base 2) to a fixed point multiplier.
+/// Converts a fixed point multiplier to a scale (log base 2).
 pub fn multiplier_to_scale(mult: f64) -> crate::Scale {
     mult.log2().round() as crate::Scale
 }
@@ -312,6 +311,9 @@ pub fn new_op_from_onnx(
     let mut deleted_indices = vec![];
     let node = match node.op().name().as_ref() {
         "ShiftLeft" => {
+            if inputs.len() != 2 {
+                return Err(GraphError::InvalidDims(idx, "shift left".to_string()));
+            };
             // load shift amount
             if let Some(c) = inputs[1].opkind().get_mutable_constant() {
                 inputs[1].decrement_use();
@@ -324,10 +326,13 @@ pub fn new_op_from_onnx(
                     out_scale: Some(input_scales[0] - raw_values[0] as i32),
                 })
             } else {
-                return Err(GraphError::OpMismatch(idx, "ShiftLeft".to_string()));
+                return Err(GraphError::OpMismatch(idx, "shift left".to_string()));
             }
         }
         "ShiftRight" => {
+            if inputs.len() != 2 {
+                return Err(GraphError::InvalidDims(idx, "shift right".to_string()));
+            };
             // load shift amount
             if let Some(c) = inputs[1].opkind().get_mutable_constant() {
                 inputs[1].decrement_use();
@@ -340,7 +345,7 @@ pub fn new_op_from_onnx(
                     out_scale: Some(input_scales[0] + raw_values[0] as i32),
                 })
             } else {
-                return Err(GraphError::OpMismatch(idx, "ShiftRight".to_string()));
+                return Err(GraphError::OpMismatch(idx, "shift right".to_string()));
             }
         }
         "MultiBroadcastTo" => {
@@ -363,7 +368,10 @@ pub fn new_op_from_onnx(
                 }
             }
 
-            assert_eq!(input_ops.len(), 3, "Range requires 3 inputs");
+            if input_ops.len() != 3 {
+                return Err(GraphError::InvalidDims(idx, "range".to_string()));
+            }
+
             let input_ops = input_ops
                 .iter()
                 .map(|x| x.get_constant().ok_or(GraphError::NonConstantRange))
@@ -419,6 +427,10 @@ pub fn new_op_from_onnx(
             if let Some(c) = inputs[1].opkind().get_mutable_constant() {
                 inputs[1].decrement_use();
                 deleted_indices.push(inputs.len() - 1);
+                if inputs[0].out_dims().is_empty() || inputs[0].out_dims()[0].len() <= axis {
+                    return Err(GraphError::InvalidDims(idx, "gather".to_string()));
+                }
+
                 op = SupportedOp::Hybrid(crate::circuit::ops::hybrid::HybridOp::Gather {
                     dim: axis,
                     constant_idx: Some(c.raw_values.map(|x| {
@@ -447,8 +459,17 @@ pub fn new_op_from_onnx(
         "Topk" => {
             let op = load_op::<Topk>(node.op(), idx, node.op().name().to_string())?;
             let axis = op.axis;
+
+            if inputs.len() != 2 {
+                return Err(GraphError::InvalidDims(idx, "topk".to_string()));
+            };
+
             // if param_visibility.is_public() {
             let k = if let Some(c) = inputs[1].opkind().get_mutable_constant() {
+                if c.raw_values.len() != 1 {
+                    return Err(GraphError::InvalidDims(idx, "topk".to_string()));
+                }
+
                 inputs[1].decrement_use();
                 deleted_indices.push(inputs.len() - 1);
                 c.raw_values.map(|x| x as usize)[0]
@@ -488,6 +509,10 @@ pub fn new_op_from_onnx(
             if let Some(c) = inputs[1].opkind().get_mutable_constant() {
                 inputs[1].decrement_use();
                 deleted_indices.push(1);
+                if c.raw_values.is_empty() {
+                    return Err(GraphError::InvalidDims(idx, "scatter elements".to_string()));
+                }
+
                 op = SupportedOp::Linear(crate::circuit::ops::poly::PolyOp::ScatterElements {
                     dim: axis,
                     constant_idx: Some(c.raw_values.map(|x| x as usize)),
@@ -522,6 +547,9 @@ pub fn new_op_from_onnx(
             if let Some(c) = inputs[1].opkind().get_mutable_constant() {
                 inputs[1].decrement_use();
                 deleted_indices.push(1);
+                if c.raw_values.is_empty() {
+                    return Err(GraphError::InvalidDims(idx, "scatter nd".to_string()));
+                }
                 op = SupportedOp::Linear(crate::circuit::ops::poly::PolyOp::ScatterND {
                     constant_idx: Some(c.raw_values.map(|x| x as usize)),
                 })
@@ -555,6 +583,9 @@ pub fn new_op_from_onnx(
             if let Some(c) = inputs[1].opkind().get_mutable_constant() {
                 inputs[1].decrement_use();
                 deleted_indices.push(1);
+                if c.raw_values.is_empty() {
+                    return Err(GraphError::InvalidDims(idx, "gather nd".to_string()));
+                }
                 op = SupportedOp::Linear(crate::circuit::ops::poly::PolyOp::GatherND {
                     batch_dims,
                     indices: Some(c.raw_values.map(|x| x as usize)),
@@ -589,6 +620,9 @@ pub fn new_op_from_onnx(
             if let Some(c) = inputs[1].opkind().get_mutable_constant() {
                 inputs[1].decrement_use();
                 deleted_indices.push(1);
+                if c.raw_values.is_empty() {
+                    return Err(GraphError::InvalidDims(idx, "gather elements".to_string()));
+                }
                 op = SupportedOp::Linear(crate::circuit::ops::poly::PolyOp::GatherElements {
                     dim: axis,
                     constant_idx: Some(c.raw_values.map(|x| x as usize)),
@@ -684,7 +718,9 @@ pub fn new_op_from_onnx(
             };
             let op = load_op::<Reduce>(node.op(), idx, node.op().name().to_string())?;
             let axes: Vec<usize> = op.axes.into_iter().collect();
-            assert_eq!(axes.len(), 1, "only support argmax over one axis");
+            if axes.len() != 1 {
+                return Err(GraphError::InvalidDims(idx, "argmax".to_string()));
+            }
 
             SupportedOp::Hybrid(HybridOp::ReduceArgMax { dim: axes[0] })
         }
@@ -694,7 +730,9 @@ pub fn new_op_from_onnx(
             };
             let op = load_op::<Reduce>(node.op(), idx, node.op().name().to_string())?;
             let axes: Vec<usize> = op.axes.into_iter().collect();
-            assert_eq!(axes.len(), 1, "only support argmin over one axis");
+            if axes.len() != 1 {
+                return Err(GraphError::InvalidDims(idx, "argmin".to_string()));
+            }
 
             SupportedOp::Hybrid(HybridOp::ReduceArgMin { dim: axes[0] })
         }
@@ -803,6 +841,9 @@ pub fn new_op_from_onnx(
             }
         }
         "Recip" => {
+            if inputs.len() != 1 {
+                return Err(GraphError::InvalidDims(idx, "recip".to_string()));
+            };
             let in_scale = input_scales[0];
             let max_scale = std::cmp::max(scales.get_max(), in_scale);
             // If the input scale is larger than the params scale
@@ -846,6 +887,9 @@ pub fn new_op_from_onnx(
             scale: scale_to_multiplier(input_scales[0]).into(),
         }),
         "Rsqrt" => {
+            if input_scales.len() != 1 {
+                return Err(GraphError::InvalidDims(idx, "rsqrt".to_string()));
+            };
             let in_scale = input_scales[0];
             let max_scale = std::cmp::max(scales.get_max(), in_scale);
             SupportedOp::Hybrid(HybridOp::Rsqrt {
@@ -933,7 +977,9 @@ pub fn new_op_from_onnx(
             let op = load_op::<Cast>(node.op(), idx, node.op().name().to_string())?;
             let dt = op.to;
 
-            assert_eq!(input_scales.len(), 1);
+            if input_scales.len() != 1 {
+                return Err(GraphError::InvalidDims(idx, "cast".to_string()));
+            };
 
             match dt {
                 DatumType::Bool
@@ -983,6 +1029,11 @@ pub fn new_op_from_onnx(
 
             if const_idx.len() == 1 {
                 let const_idx = const_idx[0];
+
+                if inputs.len() <= const_idx {
+                    return Err(GraphError::InvalidDims(idx, "mul".to_string()));
+                }
+
                 if let Some(c) = inputs[const_idx].opkind().get_mutable_constant() {
                     if c.raw_values.len() == 1 && c.raw_values[0] < 1. {
                         // if not divisible by 2 then we need to add a range check
@@ -1057,6 +1108,9 @@ pub fn new_op_from_onnx(
                     return Err(GraphError::OpMismatch(idx, "softmax".to_string()));
                 }
             };
+            if input_scales.len() != 1 {
+                return Err(GraphError::InvalidDims(idx, "softmax".to_string()));
+            }
 
             let in_scale = input_scales[0];
             let max_scale = std::cmp::max(scales.get_max(), in_scale);
@@ -1096,22 +1150,42 @@ pub fn new_op_from_onnx(
                 pool_dims: kernel_shape.to_vec(),
             })
         }
-        "Ceil" => SupportedOp::Hybrid(HybridOp::Ceil {
-            scale: scale_to_multiplier(input_scales[0]).into(),
-            legs: run_args.decomp_legs,
-        }),
-        "Floor" => SupportedOp::Hybrid(HybridOp::Floor {
-            scale: scale_to_multiplier(input_scales[0]).into(),
-            legs: run_args.decomp_legs,
-        }),
-        "Round" => SupportedOp::Hybrid(HybridOp::Round {
-            scale: scale_to_multiplier(input_scales[0]).into(),
-            legs: run_args.decomp_legs,
-        }),
-        "RoundHalfToEven" => SupportedOp::Hybrid(HybridOp::RoundHalfToEven {
-            scale: scale_to_multiplier(input_scales[0]).into(),
-            legs: run_args.decomp_legs,
-        }),
+        "Ceil" => {
+            if input_scales.len() != 1 {
+                return Err(GraphError::InvalidDims(idx, "ceil".to_string()));
+            }
+            SupportedOp::Hybrid(HybridOp::Ceil {
+                scale: scale_to_multiplier(input_scales[0]).into(),
+                legs: run_args.decomp_legs,
+            })
+        }
+        "Floor" => {
+            if input_scales.len() != 1 {
+                return Err(GraphError::InvalidDims(idx, "floor".to_string()));
+            }
+            SupportedOp::Hybrid(HybridOp::Floor {
+                scale: scale_to_multiplier(input_scales[0]).into(),
+                legs: run_args.decomp_legs,
+            })
+        }
+        "Round" => {
+            if input_scales.len() != 1 {
+                return Err(GraphError::InvalidDims(idx, "round".to_string()));
+            }
+            SupportedOp::Hybrid(HybridOp::Round {
+                scale: scale_to_multiplier(input_scales[0]).into(),
+                legs: run_args.decomp_legs,
+            })
+        }
+        "RoundHalfToEven" => {
+            if input_scales.len() != 1 {
+                return Err(GraphError::InvalidDims(idx, "roundhalftoeven".to_string()));
+            }
+            SupportedOp::Hybrid(HybridOp::RoundHalfToEven {
+                scale: scale_to_multiplier(input_scales[0]).into(),
+                legs: run_args.decomp_legs,
+            })
+        }
         "Sign" => SupportedOp::Linear(PolyOp::Sign),
         "Pow" => {
             // Extract the slope layer hyperparams from a const
@@ -1121,7 +1195,9 @@ pub fn new_op_from_onnx(
                 inputs[1].decrement_use();
                 deleted_indices.push(1);
                 if c.raw_values.len() > 1 {
-                    unimplemented!("only support scalar pow")
+                    return Err(GraphError::NonScalarPower);
+                } else if c.raw_values.is_empty() {
+                    return Err(GraphError::InvalidDims(idx, "pow".to_string()));
                 }
 
                 let exponent = c.raw_values[0];
@@ -1138,7 +1214,9 @@ pub fn new_op_from_onnx(
                 inputs[0].decrement_use();
                 deleted_indices.push(0);
                 if c.raw_values.len() > 1 {
-                    unimplemented!("only support scalar base")
+                    return Err(GraphError::NonScalarBase);
+                } else if c.raw_values.is_empty() {
+                    return Err(GraphError::InvalidDims(idx, "pow".to_string()));
                 }
 
                 let base = c.raw_values[0];
@@ -1148,25 +1226,30 @@ pub fn new_op_from_onnx(
                     base: base.into(),
                 })
             } else {
-                unimplemented!("only support constant base or pow for now")
+                return Err(GraphError::InvalidDims(idx, "pow".to_string()));
             }
         }
         "Div" => {
+            if inputs.len() != 2 {
+                return Err(GraphError::InvalidDims(idx, "div".to_string()));
+            }
+
             let const_idx = inputs
                 .iter()
                 .enumerate()
                 .filter(|(_, n)| n.is_constant())
                 .map(|(i, _)| i)
                 .collect::<Vec<_>>();
 
-            if const_idx.len() > 1 {
+            if const_idx.len() > 1 || const_idx.is_empty() {
                 return Err(GraphError::InvalidDims(idx, "div".to_string()));
             }
 
             let const_idx = const_idx[0];
-
             if const_idx != 1 {
-                unimplemented!("only support div with constant as second input")
+                return Err(GraphError::MisformedParams(
+                    "only support div with constant as second input".to_string(),
+                ));
             }
 
             if let Some(c) = inputs[const_idx].opkind().get_mutable_constant() {
@@ -1180,10 +1263,14 @@ pub fn new_op_from_onnx(
                         denom: denom.into(),
                     })
                 } else {
-                    unimplemented!("only support non zero divisors of size 1")
+                    return Err(GraphError::MisformedParams(
+                        "only support non zero divisors of size 1".to_string(),
+                    ));
                 }
             } else {
-                unimplemented!("only support div with constant as second input")
+                return Err(GraphError::MisformedParams(
+                    "only support div with constant as second input".to_string(),
+                ));
             }
         }
         "Cube" => SupportedOp::Linear(PolyOp::Pow(3)),
@@ -1323,7 +1410,7 @@ pub fn new_op_from_onnx(
             if !resize_node.contains("interpolator: Nearest")
                 && !resize_node.contains("nearest: Floor")
             {
-                unimplemented!("Only nearest neighbor interpolation is supported")
+                return Err(GraphError::InvalidInterpolation);
             }
             // check if optional scale factor is present
             if inputs.len() != 2 && inputs.len() != 3 {
@@ -1427,6 +1514,10 @@ pub fn new_op_from_onnx(
             SupportedOp::Linear(PolyOp::Reshape(output_shape))
         }
         "Flatten" => {
+            if inputs.len() != 1 || inputs[0].out_dims().is_empty() {
+                return Err(GraphError::InvalidDims(idx, "flatten".to_string()));
+            };
+
             let new_dims: Vec<usize> = vec![inputs[0].out_dims()[0].iter().product::<usize>()];
             SupportedOp::Linear(PolyOp::Flatten(new_dims))
         }
@@ -1546,6 +1637,7 @@ pub fn homogenize_input_scales(
 }
 
 #[cfg(test)]
+/// tests for the utility module
 pub mod tests {
 
     use super::*;
```

### tests/py_integration_tests.rs
```diff
@@ -72,11 +72,10 @@ mod py_tests {
                     "torchtext==0.17.2",
                     "torchvision==0.17.2",
                     "pandas==2.2.1",
-                    "numpy==1.26.4",
                     "seaborn==0.13.2",
                     "notebook==7.1.2",
                     "nbconvert==7.16.3",
-                    "onnx==1.16.0",
+                    "onnx==1.17.0",
                     "kaggle==1.6.8",
                     "py-solc-x==2.0.3",
                     "web3==7.5.0",
@@ -90,12 +89,13 @@ mod py_tests {
                     "xgboost==2.0.3",
                     "hummingbird-ml==0.4.11",
                     "lightgbm==4.3.0",
+                    "numpy==1.26.4",
                 ])
                 .status()
                 .expect("failed to execute process");
             assert!(status.success());
             let status = Command::new("pip")
-                .args(["install", "numpy==1.23"])
+                .args(["install", "numpy==1.26.4"])
                 .status()
                 .expect("failed to execute process");
 
```
