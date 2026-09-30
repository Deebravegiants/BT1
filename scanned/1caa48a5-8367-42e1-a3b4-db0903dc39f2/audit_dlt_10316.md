# [?] Fix race condition in test

## Summary
Severity: Unknown
Chain: Secret
Component: scrtlabs/SecretNetwork
Published: 2024-07-30
Source: https://github.com/scrtlabs/SecretNetwork/commit/a8cbe85e75c24bcd6325390f4c2345ba0899a0f5
Type: security-commit

## Details
Fix race condition in test

## Patch
### integration-tests/test.ts
```diff
@@ -390,16 +390,22 @@ describe("Env", () => {
 
           let txs = await Promise.all(txProm);
 
+          let count_vals = ["-1", "-1"];
           for (let i = 0; i < 2; i++) {
             if (txs[i].code !== TxResultCode.Success) {
               console.error(txs[i].rawLog);
             }
 
             expect(txs[i].code).toBe(TxResultCode.Success);
 
-            expect(getValueFromEvents(txs[i].events, "wasm-count.count-val")).toBe(String(i));
-            expect(getValueFromEvents(txs[i].events, "wasm-count.count-val", 3).length).toBe(0);
+            count_vals[i] = getValueFromEvents(txs[i].events, "wasm-count.count-val");
+            expect(getValueFromEvents(txs[i].events, "wasm-count.count-val", 2).length).toBe(0);
           }
+          if (Number(count_vals[0]) > Number(count_vals[1])) {
+            [count_vals[0], count_vals[1]] = [count_vals[1], count_vals[0]];
+          }
+          expect(count_vals[0]).toBe("0");
+          expect(count_vals[1]).toBe("1");
 
           if (success) {
             break;
```
