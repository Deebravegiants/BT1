# [?] fix: no panic for sig bit truncation (#458)

## Summary
Severity: Unknown
Chain: ZK
Component: zkonduit/ezkl
Published: 2023-09-04
Source: https://github.com/zkonduit/ezkl/commit/86ee6980d462a3dbab32db3f203c6e1ca7ab5dfe
Type: security-commit

## Details
fix: no panic for sig bit truncation (#458)

## Patch
### src/execute.rs
```diff
@@ -608,23 +608,28 @@ pub(crate) async fn calibrate(
 
                 let original_settings = settings.clone();
 
-                let mut circuit = GraphCircuit::from_run_args(&local_run_args, &model_path)
-                    .map_err(|_| "failed to create circuit from run args")
-                    .unwrap();
+                let mut circuit = match GraphCircuit::from_run_args(&local_run_args, &model_path) {
+                    Ok(c) => c,
+                    Err(_) => {
+                        return tokio::task::spawn(async move {
+                            Err(format!("failed to create circuit from run args"))
+                                as Result<GraphSettings, String>
+                        })
+                    }
+                };
 
                 tokio::task::spawn(async move {
                     let data = circuit
                         .load_graph_input(&chunk)
                         .await
-                        .map_err(|_| "failed to load circuit inputs")
-                        .unwrap();
+                        .map_err(|e| format!("failed to load circuit inputs: {}", e))?;
 
                     loop {
                         // ensures we have converged
                         let params_before = circuit.settings.clone();
                         circuit
                             .calibrate(&data)
-                            .map_err(|_| "failed to calibrate")?;
+                            .map_err(|e| format!("failed to calibrate: {}", e))?;
                         let params_after = circuit.settings.clone();
                         if params_before == params_after {
                             break;
@@ -649,10 +654,10 @@ pub(crate) async fn calibrate(
                         ..original_settings.clone()
                     };
 
-                    Ok(found_settings) as Result<GraphSettings, &str>
+                    Ok(found_settings) as Result<GraphSettings, String>
                 })
             })
-            .collect::<Vec<tokio::task::JoinHandle<std::result::Result<GraphSettings, &str>>>>();
+            .collect::<Vec<tokio::task::JoinHandle<std::result::Result<GraphSettings, String>>>>();
 
         let mut res: Vec<GraphSettings> = vec![];
         for task in tasks {
```

### src/graph/utilities.rs
```diff
@@ -1076,9 +1076,19 @@ pub fn quantize_tensor<F: PrimeField + TensorType + PartialOrd>(
     scale: u32,
     visibility: Visibility,
 ) -> Result<Tensor<F>, Box<dyn std::error::Error>> {
-    let mut value: Tensor<F> = const_value.map(|x| {
-        crate::fieldutils::i128_to_felt::<F>(quantize_float(&x.into(), 0.0, scale).unwrap())
-    });
+    let value: Result<Vec<F>, Box<dyn std::error::Error>> = const_value
+        .iter()
+        .map(|x| {
+            Ok(crate::fieldutils::i128_to_felt::<F>(quantize_float(
+                &(*x).into(),
+                0.0,
+                scale,
+            )?))
+        })
+        .collect();
+
+    let mut value: Tensor<F> = value?.into_iter().into();
+    value.reshape(&const_value.dims());
     value.set_scale(scale);
     value.set_visibility(visibility);
     Ok(value)
```

### src/tensor/mod.rs
```diff
@@ -46,7 +46,7 @@ pub enum TensorError {
     #[error("wrong method called")]
     WrongMethod,
     /// Significant bit truncation when instantiating
-    #[error("Significant bit truncation when instantiating")]
+    #[error("Significant bit truncation when instantiating, try lowering the scale")]
     SigBitTruncationError,
 }
 
```
