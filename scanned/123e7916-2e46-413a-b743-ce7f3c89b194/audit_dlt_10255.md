# [?] sec: fix 2 vulnerability (#3654)

## Summary
Severity: Unknown
Chain: Rabby
Component: RabbyHub/Rabby
Published: 2026-04-17
Source: https://github.com/RabbyHub/Rabby/commit/a752e1fcfa5500f0f49ab9558bebca9c1cf5f62b
Type: security-commit

## Details
sec: fix 2 vulnerability (#3654)

* sec: fix personal_sign hex2Text

* sec: normalize NativeMetaTransaction typedData before parseCommon & parseAction

## Patch
### src/ui/utils/index.ts
```diff
@@ -61,7 +61,7 @@ export const hex2Text = (hex: string) => {
   try {
     return hex.startsWith('0x')
       ? decodeURIComponent(
-          hex.replace(/^0x/, '').replace(/[0-9a-f]{2}/g, '%$&')
+          hex.replace(/^0x/, '').replace(/[0-9a-fA-F]{2}/g, '%$&')
         )
       : hex;
   } catch {
```

### src/ui/views/Approval/components/SignTypedData.tsx
```diff
@@ -83,6 +83,51 @@ interface SignTypedDataProps {
   $ctx?: any;
 }
 
+const POLYGON_CHAIN_ID = 137;
+const POLYGON_META_TRANSACTION_PRIMARY_TYPES = new Set([
+  'MetaTransaction',
+  'NativeMetaTransaction',
+]);
+
+// Polygon legacy meta transactions may encode the chain as domain.salt instead
+// of domain.chainId. We only patch the typed-data copy used for parsing/display.
+const normalizePolygonMetaTransactionTypedData = (
+  typedData: Record<string, any> | null
+) => {
+  if (
+    !typedData?.domain ||
+    typedData.domain.chainId ||
+    !typedData.domain.salt ||
+    !typedData.message?.functionSignature
+  ) {
+    return typedData;
+  }
+
+  const primaryType = typedData.primaryType;
+  const hasMetaTransactionShape =
+    POLYGON_META_TRANSACTION_PRIMARY_TYPES.has(primaryType) ||
+    typedData.types?.[primaryType]?.some(
+      (field) => field?.name === 'functionSignature'
+    );
+  if (!hasMetaTransactionShape) {
+    return typedData;
+  }
+
+  let chainId: number;
+  try {
+    chainId = Number(BigInt(typedData.domain.salt));
+  } catch (error) {
+    return typedData;
+  }
+  if (chainId !== POLYGON_CHAIN_ID) {
+    return typedData;
+  }
+
+  const normalizedTypedData = cloneDeep(typedData);
+  normalizedTypedData.domain.chainId = chainId;
+  return normalizedTypedData;
+};
+
 const SignTypedData = ({
   params,
   account,
@@ -217,6 +262,10 @@ const SignTypedData = ({
     }
     return [null, null];
   }, [data, isSignTypedDataV1]);
+  const normalizedSignTypedData = useMemo(
+    () => normalizePolygonMetaTransactionTypedData(signTypedData),
+    [signTypedData]
+  );
 
   useEffect(() => {
     try {
@@ -248,10 +297,10 @@ const SignTypedData = ({
   }, []);
 
   const chain = useMemo(() => {
-    if (!isSignTypedDataV1 && signTypedData) {
+    if (!isSignTypedDataV1 && normalizedSignTypedData) {
       let chainId;
       try {
-        chainId = signTypedData?.domain?.chainId;
+        chainId = normalizedSignTypedData?.domain?.chainId;
       } catch (error) {
         console.error(error);
       }
@@ -261,7 +310,7 @@ const SignTypedData = ({
     }
 
     return undefined;
-  }, [data, isSignTypedDataV1, signTypedData]);
+  }, [data, isSignTypedDataV1, normalizedSignTypedData]);
 
   const getCurrentChainId = async () => {
     if (params.session.origin !== INTERNAL_REQUEST_ORIGIN) {
@@ -289,19 +338,19 @@ const SignTypedData = ({
         wallet.clearGnosisMessage();
       }
     }
-    if (!isSignTypedDataV1 && signTypedData) {
-      const chainId = signTypedData?.domain?.chainId;
+    if (!isSignTypedDataV1 && normalizedSignTypedData) {
+      const chainId = normalizedSignTypedData?.domain?.chainId;
       if (isTestnetChainId(chainId)) {
         return null;
       }
       return wallet.openapi.parseCommon({
-        typed_data: signTypedData,
+        typed_data: normalizedSignTypedData,
         user_addr: currentAccount!.address,
         origin: session.origin,
       });
     }
     return;
-  }, [data, isSignTypedDataV1, signTypedData]);
+  }, [data, isSignTypedDataV1, normalizedSignTypedData]);
 
   if (error) {
     console.error('error', error);
@@ -719,7 +768,7 @@ const SignTypedData = ({
             parseAction({
               type: 'typed_data',
               data: action as TypeDataActionItem,
-              typedData: signTypedData,
+              typedData: normalizedSignTypedData,
               sender,
               balanceChange:
                 typedDataActionData.pre_exec_result?.balance_change,
@@ -754,7 +803,7 @@ const SignTypedData = ({
           const parsed = parseAction({
             type: 'typed_data',
             data: typedDataActionData.action as any,
-            typedData: signTypedData,
+            typedData: normalizedSignTypedData,
             sender,
             balanceChange: typedDataActionData.pre_exec_result?.balance_change,
             preExecVersion:
@@ -780,7 +829,13 @@ const SignTypedData = ({
         setIsLoading(false);
       }
     }
-  }, [loading, typedDataActionData, signTypedData, params, isSignTypedDataV1]);
+  }, [
+    loading,
+    typedDataActionData,
+    normalizedSignTypedData,
+    params,
+    isSignTypedDataV1,
+  ]);
 
   useEffect(() => {
     if (scrollRef.current && scrollInfo && scrollRefSize) {
```
