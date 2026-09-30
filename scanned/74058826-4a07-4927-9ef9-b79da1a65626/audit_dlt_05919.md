# [?] fix: dynamically load WASM provider to avoid TextDecoder crash in React Native debug builds

## Summary
Severity: Unknown
Chain: WalletConnect
Component: WalletConnect/walletconnect-monorepo
Published: 2026-02-13
Source: https://github.com/WalletConnect/walletconnect-monorepo/commit/c1131bd8acd6fcaef2c465b14cd538117f0e2ab8
Type: security-commit

## Details
fix: dynamically load WASM provider to avoid TextDecoder crash in React Native debug builds

The WASM provider and its dependencies (brotli, yttrium binary) were
statically imported, causing TextDecoder-dependent code to load even in
React Native where it is unavailable in debug builds. The WASM module
is now loaded via dynamic import() only when not in a React Native
environment.

Co-authored-by: Cursor <cursoragent@cursor.com>

## Patch
### packages/pay/src/client.ts
```diff
@@ -35,7 +35,7 @@ export class WalletConnectPay {
   public readonly baseUrl: string;
 
   private readonly logger: Logger;
-  private readonly provider: PayProvider;
+  private readonly providerPromise: Promise<PayProvider>;
 
   /**
    * Initialize a new Pay client
@@ -68,9 +68,10 @@ export class WalletConnectPay {
       bundleId: getAppId() ?? "",
     };
 
-    // Create provider (auto-detects available provider)
-    this.provider = createProvider(providerConfig);
-    this.logger.debug(`${LOGGER_CONTEXT} provider initialized`);
+    this.providerPromise = createProvider(providerConfig);
+    this.providerPromise.then(() => {
+      this.logger.debug(`${LOGGER_CONTEXT} provider initialized`);
+    });
   }
 
   /**
@@ -101,7 +102,8 @@ export class WalletConnectPay {
     );
 
     try {
-      const response = await this.provider.getPaymentOptions(params);
+      const provider = await this.providerPromise;
+      const response = await provider.getPaymentOptions(params);
 
       this.logger.debug(
         { paymentId: response.paymentId, optionsCount: response.options.length },
@@ -131,7 +133,8 @@ export class WalletConnectPay {
     );
 
     try {
-      const actions = await this.provider.getRequiredPaymentActions(params);
+      const provider = await this.providerPromise;
+      const actions = await provider.getRequiredPaymentActions(params);
 
       this.logger.debug(
         { actionsCount: actions.length },
@@ -168,7 +171,8 @@ export class WalletConnectPay {
     );
 
     try {
-      const response = await this.provider.confirmPayment(params);
+      const provider = await this.providerPromise;
+      const response = await provider.confirmPayment(params);
 
       this.logger.debug(
         { status: response.status, isFinal: response.isFinal },
```

### packages/pay/src/providers/index.ts
```diff
@@ -1,25 +1,36 @@
 /**
  * Provider exports for WalletConnect Pay SDK
+ *
+ * WASM provider is loaded dynamically to avoid pulling in TextDecoder-dependent
+ * code in React Native debug builds where TextDecoder is unavailable.
  */
 
+import { isReactNative } from "@walletconnect/utils";
 import type { PayProvider, PayProviderConfig, PayProviderType } from "../types/index.js";
 import { createNativeProvider, isNativeProviderAvailable } from "./native.js";
-import { createWasmProvider, isWasmProviderAvailable } from "./wasm.js";
 
 export * from "./native.js";
-export * from "./wasm.js";
+
+function isWasmProviderAvailable(): boolean {
+  return !isReactNative() && typeof WebAssembly !== "undefined";
+}
+
+export { isWasmProviderAvailable };
+
+async function loadWasmProvider(config: PayProviderConfig): Promise<PayProvider> {
+  const { createWasmProvider } = await import("./wasm.js");
+  return createWasmProvider(config);
+}
 
 /**
  * Detect the best available provider type for the current environment
  * Priority: Native (React Native) > WASM (Browser/Node.js)
  */
 export function detectProviderType(): PayProviderType | null {
-  // Check for native module (React Native) - preferred for mobile
   if (isNativeProviderAvailable()) {
     return "native";
   }
 
-  // Check for WASM support (Browser/Node.js)
   if (isWasmProviderAvailable()) {
     return "wasm";
   }
@@ -28,26 +39,33 @@ export function detectProviderType(): PayProviderType | null {
 }
 
 /**
- * Create a provider based on auto-detection
- * @param config - Provider configuration
+ * Create a provider based on auto-detection.
+ * Returns a Promise because the WASM provider is loaded dynamically.
  */
-export function createProvider(config: PayProviderConfig): PayProvider {
-  const providerType = detectProviderType();
+export function createProvider(config: PayProviderConfig): Promise<PayProvider> {
+  return new Promise((resolve, reject) => {
+    const providerType = detectProviderType();
 
-  if (!providerType) {
-    throw new Error(
-      "No Pay provider available. Make sure you are running in React Native with the native module installed, or in a browser/Node.js environment with WebAssembly support.",
-    );
-  }
+    if (!providerType) {
+      reject(
+        new Error(
+          "No Pay provider available. Make sure you are running in React Native with the native module installed, or in a browser/Node.js environment with WebAssembly support.",
+        ),
+      );
+      return;
+    }
 
-  switch (providerType) {
-    case "native":
-      return createNativeProvider(config);
-    case "wasm":
-      return createWasmProvider(config);
-    default:
-      throw new Error(`Unknown provider type: ${providerType}`);
-  }
+    switch (providerType) {
+      case "native":
+        resolve(createNativeProvider(config));
+        break;
+      case "wasm":
+        resolve(loadWasmProvider(config));
+        break;
+      default:
+        reject(new Error(`Unknown provider type: ${providerType}`));
+    }
+  });
 }
 
 /**
```
