# [?] fix: edit fibonacci example to use `u128` and note overflow case in quickstart (#245)

## Summary
Severity: Unknown
Chain: ZK
Component: succinctlabs/sp1
Published: 2024-02-16
Source: https://github.com/succinctlabs/sp1/commit/e19f74222f66bb83aeb56f3a4d022a55bbfac793
Type: security-commit

## Details
fix: edit fibonacci example to use `u128` and note overflow case in quickstart (#245)

## Patch
### book/getting-started/quickstart.md
```diff
@@ -69,11 +69,11 @@ The output should show
     Compiling fibonacci-script v0.1.0 (/Users/umaroy/Documents/fibonacci/script)
     Finished release [optimized] target(s) in 26.14s
     Running `target/release/fibonacci-script`
-a: 3867074829
-b: 2448710421
+a: 205697230343233228174223751303346572685
+b: 332825110087067562321196029789634457848
 succesfully generated and verified proof for the program!
 ```
 
-The program by default is quite small, so proof generation will only take a few seconds locally. After it completes, the proof will be saved in the `proof-with-pis.json` file and also be verified for correctness.
+The program by default is quite small, so proof generation will only take a few seconds locally. After it completes, the proof will be saved in the `proof-with-io.json` file and also be verified for correctness.
 
-You can play around with how many rounds of Fibonacci are executed by playing around with `n` (by default set to `500`) in the file `script/src/main.rs`.
\ No newline at end of file
+You can play around with how many rounds of Fibonacci are executed by playing around with `n` (by default set to `186`) in the file `script/src/main.rs`. Integer overflow will cause larger `n` to result in non-fibonacci output, although the proof will still be generated and verified.
\ No newline at end of file
```

### cli/src/assets/program/main.rs
```diff
@@ -4,10 +4,13 @@
 sp1_zkvm::entrypoint!(main);
 
 pub fn main() {
+    // NOTE: values of n larger than 186 will overflow the u128 type,
+    // resulting in output that doesn't match fibonacci sequence.
+    // However, the resulting proof will still be valid!
     let n = sp1_zkvm::io::read::<u32>();
-    let mut a = 0;
-    let mut b = 1;
-    let mut sum;
+    let mut a: u128 = 0;
+    let mut b: u128 = 1;
+    let mut sum: u128;
     for _ in 1..n {
         sum = a + b;
         a = b;
```

### cli/src/assets/script/main.rs
```diff
@@ -7,13 +7,13 @@ const ELF: &[u8] = include_bytes!("../../program/elf/riscv32im-succinct-zkvm-elf
 fn main() {
     // Generate proof.
     let mut stdin = SP1Stdin::new();
-    let n = 500u32;
+    let n = 186u32;
     stdin.write(&n);
     let mut proof = SP1Prover::prove(ELF, stdin).expect("proving failed");
 
     // Read output.
-    let a = proof.stdout.read::<u32>();
-    let b = proof.stdout.read::<u32>();
+    let a = proof.stdout.read::<u128>();
+    let b = proof.stdout.read::<u128>();
     println!("a: {}", a);
     println!("b: {}", b);
 
```
