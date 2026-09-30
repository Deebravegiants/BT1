# [?] CORDA-3831: Prevent CordappImpl TEST_INSTANCE crashing node when PWD is file-system root directory. (#6360)

## Summary
Severity: Unknown
Chain: Corda
Component: corda/corda
Published: 2020-06-17
Source: https://github.com/corda/corda/commit/0f1bfb13dab98af32cd803c3c40c988906e32ecd
Type: security-commit

## Details
CORDA-3831: Prevent CordappImpl TEST_INSTANCE crashing node when PWD is file-system root directory. (#6360)

## Patch
### core/src/main/kotlin/net/corda/core/internal/cordapp/CordappImpl.kt
```diff
@@ -47,7 +47,7 @@ data class CordappImpl(
     }
 
     companion object {
-        fun jarName(url: URL): String = url.toPath().fileName.toString().removeSuffix(".jar")
+        fun jarName(url: URL): String = (url.toPath().fileName ?: "").toString().removeSuffix(".jar")
 
         /** CorDapp manifest entries */
         const val CORDAPP_CONTRACT_NAME = "Cordapp-Contract-Name"
@@ -81,7 +81,7 @@ data class CordappImpl(
                 serializationCustomSerializers = emptyList(),
                 customSchemas = emptySet(),
                 jarPath = Paths.get("").toUri().toURL(),
-                info = CordappImpl.UNKNOWN_INFO,
+                info = UNKNOWN_INFO,
                 allFlows = emptyList(),
                 jarHash = SecureHash.allOnesHash,
                 minimumPlatformVersion = 1,
```
