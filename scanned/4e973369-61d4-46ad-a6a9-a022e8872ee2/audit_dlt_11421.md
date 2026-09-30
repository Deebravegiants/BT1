# [?] fix: add slack to lookup overflow for high prec models (#590)

## Summary
Severity: Unknown
Chain: ZK
Component: zkonduit/ezkl
Published: 2023-11-04
Source: https://github.com/zkonduit/ezkl/commit/9c723f90e607ae32443c7e60c6f916f30bf7d640
Type: security-commit

## Details
fix: add slack to lookup overflow for high prec models (#590)

## Patch
### examples/notebooks/generalized_inverse.ipynb
```diff
@@ -15,7 +15,7 @@
     },
     {
       "cell_type": "code",
-      "execution_count": null,
+      "execution_count": 1,
       "id": "95613ee9",
       "metadata": {
         "id": "95613ee9"
@@ -48,7 +48,7 @@
     },
     {
       "cell_type": "code",
-      "execution_count": null,
+      "execution_count": 2,
       "id": "9LgqGF56Qcdz",
       "metadata": {
         "id": "9LgqGF56Qcdz"
@@ -69,7 +69,7 @@
     },
     {
       "cell_type": "code",
-      "execution_count": null,
+      "execution_count": 3,
       "id": "YRQLvvsXVs9s",
       "metadata": {
         "id": "YRQLvvsXVs9s"
@@ -84,7 +84,7 @@
     },
     {
       "cell_type": "code",
-      "execution_count": null,
+      "execution_count": 4,
       "id": "b37637c4",
       "metadata": {
         "id": "b37637c4"
@@ -103,15 +103,15 @@
     },
     {
       "cell_type": "code",
-      "execution_count": null,
+      "execution_count": 5,
       "id": "82db373a",
       "metadata": {
         "id": "82db373a"
       },
       "outputs": [],
       "source": [
         "# After training, export to onnx (network.onnx) and create a data file (input.json)\n",
-        "A = 0.1*torch.rand(1,*[200, 200], requires_grad=True)\n",
+        "A = 0.1*torch.rand(1,*[10, 10], requires_grad=True)\n",
         "B = A.inverse()\n",
         "\n",
         "# Flips the neural net into inference mode\n",
@@ -143,7 +143,7 @@
     },
     {
       "cell_type": "code",
-      "execution_count": null,
+      "execution_count": 6,
       "id": "HOLcdGx4eQ9n",
       "metadata": {
         "colab": {
@@ -152,14 +152,25 @@
         "id": "HOLcdGx4eQ9n",
         "outputId": "cd0a4f10-251e-492e-9f05-d8af0d79c86a"
       },
-      "outputs": [],
+      "outputs": [
+        {
+          "data": {
+            "text/plain": [
+              "tensor(True)"
+            ]
+          },
+          "execution_count": 6,
+          "metadata": {},
+          "output_type": "execute_result"
+        }
+      ],
       "source": [
         "circuit.forward(A,B)"
       ]
     },
     {
       "cell_type": "code",
-      "execution_count": null,
+      "execution_count": 7,
       "id": "d5e374a2",
       "metadata": {
         "colab": {
@@ -169,7 +180,62 @@
         "id": "d5e374a2",
         "outputId": "11ae5963-02d4-4939-9c98-d126071a9ba0"
       },
-      "outputs": [],
+      "outputs": [
+        {
+          "name": "stderr",
+          "output_type": "stream",
+          "text": [
+            "constant node with 1 use\n",
+            "constant node with 1 use\n",
+            "no verifying key provided for kzgcommit. processed value will be none\n",
+            "constant node with 1 use\n",
+            "constant node with 1 use\n",
+            "no verifying key provided for kzgcommit. processed value will be none\n",
+            "constant node with 1 use\n",
+            "constant node with 1 use\n",
+            "no verifying key provided for kzgcommit. processed value will be none\n",
+            "constant node with 1 use\n",
+            "constant node with 1 use\n",
+            "no verifying key provided for kzgcommit. processed value will be none\n",
+            "constant node with 1 use\n",
+            "constant node with 1 use\n",
+            "no verifying key provided for kzgcommit. processed value will be none\n",
+            "constant node with 1 use\n",
+            "constant node with 1 use\n",
+            "no verifying key provided for kzgcommit. processed value will be none\n",
+            "constant node with 1 use\n",
+            "constant node with 1 use\n",
+            "no verifying key provided for kzgcommit. processed value will be none\n",
+            "constant node with 1 use\n",
+            "constant node with 1 use\n",
+            "no verifying key provided for kzgcommit. processed value will be none\n",
+            "constant node with 1 use\n",
+            "constant node with 1 use\n",
+            "no verifying key provided for kzgcommit. processed value will be none\n",
+            "constant node with 1 use\n",
+            "constant node with 1 use\n",
+            "no verifying key provided for kzgcommit. processed value will be none\n",
+            "constant node with 1 use\n",
+            "constant node with 1 use\n",
+            "no verifying key provided for kzgcommit. processed value will be none\n",
+            "constant node with 1 use\n",
+            "constant node with 1 use\n",
+            "no verifying key provided for kzgcommit. processed value will be none\n",
+            "constant node with 1 use\n",
+            "constant node with 1 use\n",
+            "no verifying key provided for kzgcommit. processed value will be none\n",
+            "constant node with 1 use\n",
+            "constant node with 1 use\n",
+            "no verifying key provided for kzgcommit. processed value will be none\n",
+            "constant node with 1 use\n",
+            "constant node with 1 use\n",
+            "no verifying key provided for kzgcommit. processed value will be none\n",
+            "constant node with 1 use\n",
+            "constant node with 1 use\n",
+            "no verifying key provided for kzgcommit. processed value will be none\n"
+          ]
+        }
+      ],
       "source": [
         "\n",
         "res = ezkl.gen_settings(model_path, settings_path, py_run_args=gip_run_args)\n",
```

### src/commands.rs
```diff
@@ -250,7 +250,7 @@ pub enum Commands {
         /// Target for calibration.
         target: CalibrationTarget,
         /// Optional scales to specifically try for calibration.
-        #[arg(long, value_delimiter = ',')]
+        #[arg(long, value_delimiter = ',', allow_hyphen_values = true)]
         scales: Option<Vec<crate::Scale>>,
         /// max logrows to use for calibration, 26 is the max public SRS size
         #[arg(long)]
```

### src/graph/mod.rs
```diff
@@ -836,7 +836,7 @@ impl GraphCircuit {
         let num_cols = Table::<Fp>::num_cols_required(safe_range, max_col_size);
 
         // empirically determined that this is when performance starts to degrade significantly
-        if num_cols > 3 {
+        if num_cols > 4 {
             let err_string = format!(
                 "No possible lookup range can accomodate max value min and max value ({}, {})",
                 safe_range.0, safe_range.1
```

### src/lib.rs
```diff
@@ -79,10 +79,10 @@ pub struct RunArgs {
     #[arg(short = 'T', long, default_value = "0")]
     pub tolerance: Tolerance,
     /// The denominator in the fixed point representation used when quantizing inputs
-    #[arg(short = 'S', long, default_value = "7")]
+    #[arg(short = 'S', long, default_value = "7", allow_hyphen_values = true)]
     pub input_scale: Scale,
     /// The denominator in the fixed point representation used when quantizing parameters
-    #[arg(long, default_value = "7")]
+    #[arg(long, default_value = "7", allow_hyphen_values = true)]
     pub param_scale: Scale,
     /// if the scale is ever > scale_rebase_multiplier * input_scale then the scale is rebased to input_scale (this a more advanced parameter, use with caution)
     #[arg(long, default_value = "1")]
```
