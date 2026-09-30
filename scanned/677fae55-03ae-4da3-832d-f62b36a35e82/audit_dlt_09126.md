# [?] fix: encodeISS crash - Buffer is not of Uint8Array type

## Summary
Severity: Unknown
Chain: WalletConnect
Component: WalletConnect/walletconnect-monorepo
Published: 2023-02-21
Source: https://github.com/WalletConnect/walletconnect-monorepo/commit/63144373e252b503e69110316e83fa58eed85d26
Type: security-commit

## Details
fix: encodeISS crash - Buffer is not of Uint8Array type

## Patch
### package-lock.json
```diff
@@ -25379,7 +25379,7 @@
         "events": "^3.3.0",
         "lodash.isequal": "4.5.0",
         "pino": "7.11.0",
-        "uint8arrays": "3.1.0"
+        "uint8arrays": "^3.1.0"
       },
       "devDependencies": {
         "@types/lodash.isequal": "4.5.6"
@@ -25454,7 +25454,7 @@
         "@walletconnect/window-metadata": "^1.0.1",
         "detect-browser": "5.3.0",
         "query-string": "7.1.1",
-        "uint8arrays": "3.1.0"
+        "uint8arrays": "^3.1.0"
       },
       "devDependencies": {
         "@types/lodash.isequal": "4.5.6"
@@ -25497,7 +25497,7 @@
       "devDependencies": {
         "ethereum-test-network": "0.1.6",
         "ethers": "5.6.9",
-        "uint8arrays": "3.1.0",
+        "uint8arrays": "^3.1.0",
         "web3": "1.7.5"
       }
     },
@@ -25512,7 +25512,7 @@
         "@walletconnect/types": "2.4.4",
         "@walletconnect/utils": "2.4.4",
         "events": "^3.3.0",
-        "uint8arrays": "3.1.0"
+        "uint8arrays": "^3.1.0"
       }
     },
     "providers/universal-provider": {
@@ -25536,7 +25536,7 @@
         "cosmos-wallet": "^1.2.0",
         "ethereum-test-network": "0.1.6",
         "ethers": "5.7.0",
-        "uint8arrays": "3.0.0",
+        "uint8arrays": "^3.0.0",
         "web3": "1.7.5"
       }
     },
@@ -30310,7 +30310,7 @@
         "events": "^3.3.0",
         "lodash.isequal": "4.5.0",
         "pino": "7.11.0",
-        "uint8arrays": "3.1.0"
+        "uint8arrays": "^3.1.0"
       }
     },
     "@walletconnect/environment": {
@@ -30339,7 +30339,7 @@
         "ethereum-test-network": "0.1.6",
         "ethers": "5.6.9",
         "events": "^3.3.0",
-        "uint8arrays": "3.1.0",
+        "uint8arrays": "^3.1.0",
         "web3": "1.7.5"
       }
     },
@@ -30534,7 +30534,7 @@
         "@walletconnect/types": "2.4.4",
         "@walletconnect/utils": "2.4.4",
         "events": "^3.3.0",
-        "uint8arrays": "3.1.0"
+        "uint8arrays": "^3.1.0"
       }
     },
     "@walletconnect/time": {
@@ -30576,7 +30576,7 @@
         "ethers": "5.7.0",
         "events": "^3.3.0",
         "pino": "7.11.0",
-        "uint8arrays": "3.0.0",
+        "uint8arrays": "^3.0.0",
         "web3": "1.7.5"
       },
       "dependencies": {
@@ -30764,7 +30764,7 @@
         "@walletconnect/window-metadata": "^1.0.1",
         "detect-browser": "5.3.0",
         "query-string": "7.1.1",
-        "uint8arrays": "3.1.0"
+        "uint8arrays": "^3.1.0"
       }
     },
     "@walletconnect/web3wallet": {
```

### packages/core/package.json
```diff
@@ -45,7 +45,7 @@
     "events": "^3.3.0",
     "lodash.isequal": "4.5.0",
     "pino": "7.11.0",
-    "uint8arrays": "3.1.0"
+    "uint8arrays": "^3.1.0"
   },
   "devDependencies": {
     "@types/lodash.isequal": "4.5.6"
```

### packages/utils/package.json
```diff
@@ -44,7 +44,7 @@
     "@walletconnect/window-metadata": "^1.0.1",
     "detect-browser": "5.3.0",
     "query-string": "7.1.1",
-    "uint8arrays": "3.1.0"
+    "uint8arrays": "^3.1.0"
   },
   "devDependencies": {
     "@types/lodash.isequal": "4.5.6"
```

### providers/ethereum-provider/package.json
```diff
@@ -49,7 +49,7 @@
   "devDependencies": {
     "ethereum-test-network": "0.1.6",
     "ethers": "5.6.9",
-    "uint8arrays": "3.1.0",
+    "uint8arrays": "^3.1.0",
     "web3": "1.7.5"
   }
 }
```

### providers/signer-connection/package.json
```diff
@@ -36,6 +36,6 @@
     "@walletconnect/types": "2.4.4",
     "@walletconnect/utils": "2.4.4",
     "events": "^3.3.0",
-    "uint8arrays": "3.1.0"
+    "uint8arrays": "^3.1.0"
   }
 }
```

### providers/universal-provider/package.json
```diff
@@ -49,7 +49,7 @@
     "cosmos-wallet": "^1.2.0",
     "ethereum-test-network": "0.1.6",
     "ethers": "5.7.0",
-    "uint8arrays": "3.0.0",
+    "uint8arrays": "^3.0.0",
     "web3": "1.7.5"
   }
 }
```
