# [?] [experimental] Make the params patcher warn on negative integer overflows too

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana-web3.js
Published: 2023-03-29
Source: https://github.com/solana-foundation/solana-web3.js/commit/79b95f7fb68abeb37b06db97af7e4ea0a36bb722
Type: security-commit

## Details
[experimental] Make the params patcher warn on negative integer overflows too
## Summary

The code that patches up the params on their way to the Solana RPC warns on positive integer overflows (numeric values larger than `Number.MAX_SAFE_INTEGER`) but not on negative values. This PR fixes that, and reorganizes the tests to test the correct features at the correct levels.

## Test Plan

```
pnpm test:unit:browser
pnpm test:unit:node
```

## Patch
### packages/rpc-transport/src/__tests__/json-rpc-transport-params-patcher-test.ts
```diff
@@ -0,0 +1,40 @@
+import { IJsonRpcTransport } from '..';
+import { createJsonRpcTransport } from '../json-rpc-transport';
+import { patchParamsForSolanaLabsRpc } from '../params-patcher';
+
+jest.mock('../params-patcher');
+
+// FIXME(solana-labs/solana/issues/30341) The JSON RPC was designed to communicate JavaScript
+// `Numbers` over the wire, which puts values over `Number.MAX_SAFE_INTEGER` at risk of rounding
+// errors. This test exercises the warning handler for such integer overflows.
+describe('Solana JSON-RPC params patcher', () => {
+    let onIntegerOverflow: jest.Mock;
+    let transport: IJsonRpcTransport;
+    const url = 'fake://url';
+    beforeEach(() => {
+        onIntegerOverflow = jest.fn();
+        transport = createJsonRpcTransport({ onIntegerOverflow, url });
+    });
+    describe('when a method call results in an integer overflow', () => {
+        beforeEach(() => {
+            (patchParamsForSolanaLabsRpc as jest.Mock).mockImplementation((params, onIntegerOverflow) => {
+                onIntegerOverflow();
+                return params;
+            });
+        });
+        it('calls `onIntegerOverflow` with the offending method name', () => {
+            transport.send('someMethod', [1n]);
+            expect(onIntegerOverflow).toHaveBeenCalled();
+            expect(onIntegerOverflow.mock.calls[0][0]).toBe('someMethod');
+        });
+    });
+    describe('when a method call does not result in an integer overflow', () => {
+        beforeEach(() => {
+            (patchParamsForSolanaLabsRpc as jest.Mock).mockImplementation(params => params);
+        });
+        it('does not call `onIntegerOverflow`', () => {
+            transport.send('someMethod', [1n]);
+            expect(onIntegerOverflow).not.toHaveBeenCalled();
+        });
+    });
+});
```

### packages/rpc-transport/src/__tests__/json-rpc-transport-test.ts
```diff
@@ -23,70 +23,4 @@ describe('JSON-RPC 2.0 transport', () => {
         await expect(sendPromise).rejects.toThrow(/o no/);
         await expect(sendPromise).rejects.toMatchObject({ code: 123, data: 'abc' });
     });
-    // FIXME(solana-labs/solana/issues/30341) The JSON RPC was designed to communicate JavaScript
-    // `Numbers` over the wire, which puts values over `Number.MAX_SAFE_INTEGER` at risk of rounding
-    // errors. This test exercises the warning handler for such integer overflows.
-    describe('with respect to possible integer overflows', () => {
-        let onIntegerOverflow: jest.Mock;
-        let transport: IJsonRpcTransport;
-        beforeEach(() => {
-            onIntegerOverflow = jest.fn();
-        });
-        describe('given a transport configured without an `onIntegerOverflow` function', () => {
-            beforeEach(() => {
-                transport = createJsonRpcTransport({ url: 'fake://url' });
-            });
-            it('does not call `onIntegerOverflow` when passed a value above `Number.MAX_SAFE_INTEGER`', async () => {
-                expect.assertions(2);
-                fetchMock.once(JSON.stringify({ result: 123 }));
-                const result = await transport.send('someMethod', BigInt(Number.MAX_SAFE_INTEGER) + 1n);
-                expect(onIntegerOverflow).not.toHaveBeenCalled();
-                expect(result).toBe(123);
-            });
-        });
-        describe('given a transport configured with an `onIntegerOverflow` function', () => {
-            beforeEach(() => {
-                transport = createJsonRpcTransport({ onIntegerOverflow, url: 'fake://url' });
-            });
-            it('calls `onIntegerOverflow` when passed a value above `Number.MAX_SAFE_INTEGER`', async () => {
-                expect.assertions(2);
-                fetchMock.once(JSON.stringify({ result: 123 }));
-                const result = await transport.send('someMethod', BigInt(Number.MAX_SAFE_INTEGER) + 1n);
-                expect(onIntegerOverflow).toHaveBeenCalledWith('someMethod', [], BigInt(Number.MAX_SAFE_INTEGER) + 1n);
-                expect(result).toBe(123);
-            });
-            it('calls `onIntegerOverflow` when passed a nested array having a value above `Number.MAX_SAFE_INTEGER`', async () => {
-                expect.assertions(2);
-                fetchMock.once(JSON.stringify({ result: 123 }));
-                const result = await transport.send('someMethod', [1, 2, [3, BigInt(Number.MAX_SAFE_INTEGER) + 1n]]);
-                expect(onIntegerOverflow).toHaveBeenCalledWith(
-                    'someMethod',
-                    [2, 1], // Equivalent to `params[2][1]`.
-                    BigInt(Number.MAX_SAFE_INTEGER) + 1n
-                );
-                expect(result).toBe(123);
-            });
-            it('calls `onIntegerOverflow` when passed a nested object having a value above `Number.MAX_SAFE_INTEGER`', async () => {
-                expect.assertions(2);
-                fetchMock.once(JSON.stringify({ result: 123 }));
-                const result = await transport.send('someMethod', {
-                    a: 1,
-                    b: { b1: 2, b2: BigInt(Number.MAX_SAFE_INTEGER) + 1n },
-                });
-                expect(onIntegerOverflow).toHaveBeenCalledWith(
-                    'someMethod',
-                    ['b', 'b2'], // Equivalent to `params.b.b2`.
-                    BigInt(Number.MAX_SAFE_INTEGER) + 1n
-                );
-                expect(result).toBe(123);
-            });
-            it('does not call `onIntegerOverflow` when passed `Number.MAX_SAFE_INTEGER`', async () => {
-                expect.assertions(2);
-                fetchMock.once(JSON.stringify({ result: 123 }));
-                const result = await transport.send('someMethod', BigInt(Number.MAX_SAFE_INTEGER));
-                expect(onIntegerOverflow).not.toHaveBeenCalled();
-                expect(result).toBe(123);
-            });
-        });
-    });
 });
```

### packages/rpc-transport/src/__tests__/params-patcher-test.ts
```diff
@@ -43,4 +43,40 @@ describe('patchParamsForSolanaLabsRpc', () => {
             });
         });
     });
+    describe('with respect to integer overflows', () => {
+        let onIntegerOverflow: (keyPath: (number | string)[], value: bigint) => void;
+        beforeEach(() => {
+            onIntegerOverflow = jest.fn();
+        });
+        Object.entries({
+            'value above `Number.MAX_SAFE_INTEGER`': BigInt(Number.MAX_SAFE_INTEGER) + 1n,
+            'value below `Number.MAX_SAFE_INTEGER`': -BigInt(Number.MAX_SAFE_INTEGER) - 1n,
+        }).forEach(([description, value]) => {
+            it('calls `onIntegerOverflow` when passed a value ' + description, () => {
+                patchParamsForSolanaLabsRpc(value, onIntegerOverflow);
+                expect(onIntegerOverflow).toHaveBeenCalledWith(
+                    [], // Equivalent to `params`
+                    value
+                );
+            });
+            it('calls `onIntegerOverflow` when passed a nested array having a value ' + description, () => {
+                patchParamsForSolanaLabsRpc([1, 2, [3, value]], onIntegerOverflow);
+                expect(onIntegerOverflow).toHaveBeenCalledWith(
+                    [2, 1], // Equivalent to `params[2][1]`.
+                    value
+                );
+            });
+            it('calls `onIntegerOverflow` when passed a nested object having a value ' + description, () => {
+                patchParamsForSolanaLabsRpc({ a: 1, b: { b1: 2, b2: value } }, onIntegerOverflow);
+                expect(onIntegerOverflow).toHaveBeenCalledWith(
+                    ['b', 'b2'], // Equivalent to `params.b.b2`.
+                    value
+                );
+            });
+            it('does not call `onIntegerOverflow` when passed `Number.MAX_SAFE_INTEGER`', () => {
+                patchParamsForSolanaLabsRpc(BigInt(Number.MAX_SAFE_INTEGER), onIntegerOverflow);
+                expect(onIntegerOverflow).not.toHaveBeenCalled();
+            });
+        });
+    });
 });
```

### packages/rpc-transport/src/params-patcher.ts
```diff
@@ -22,7 +22,7 @@ function visitNode<T>(value: T, keyPath: KeyPath, onIntegerOverflow?: IntegerOve
         // FIXME(solana-labs/solana/issues/30341) Create a data type to represent u64 in the Solana
         // JSON RPC implementation so that we can throw away this entire patcher instead of unsafely
         // downcasting `bigints` to `numbers`.
-        if (onIntegerOverflow && value > Number.MAX_SAFE_INTEGER) {
+        if (onIntegerOverflow && (value > Number.MAX_SAFE_INTEGER || value < -Number.MAX_SAFE_INTEGER)) {
             onIntegerOverflow(keyPath, value);
         }
         return Number(value) as TypescriptBug33014;
```
