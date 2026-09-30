# [?] ENT-10048,ENT-10050 - Security vulnerabilities (#7397)

## Summary
Severity: Unknown
Chain: Corda
Component: corda/corda
Published: 2023-06-27
Source: https://github.com/corda/corda/commit/d02f6ff68c6b2ca2223d86966f598f76e13415b3
Type: security-commit

## Details
ENT-10048,ENT-10050 - Security vulnerabilities (#7397)

* Updated netty and tcnative

## Patch
### build.gradle
```diff
@@ -79,8 +79,8 @@ buildscript {
     ext.djvm_version = constants.getProperty("djvmVersion")
     ext.deterministic_rt_version = constants.getProperty('deterministicRtVersion')
     ext.okhttp_version = '3.14.2'
-    ext.netty_version = '4.1.46.Final'
-    ext.tcnative_version = '2.0.29.Final'
+    ext.netty_version = '4.1.77.Final'
+    ext.tcnative_version = '2.0.48.Final'
     ext.typesafe_config_version = constants.getProperty("typesafeConfigVersion")
     ext.fileupload_version = '1.4'
     ext.kryo_version = '4.0.2'
```

### node-api/src/main/kotlin/net/corda/nodeapi/internal/protonwrapper/netty/SSLHelper.kt
```diff
@@ -6,7 +6,7 @@ import io.netty.handler.ssl.SniHandler
 import io.netty.handler.ssl.SslContextBuilder
 import io.netty.handler.ssl.SslHandler
 import io.netty.handler.ssl.SslProvider
-import io.netty.util.DomainNameMappingBuilder
+import io.netty.util.DomainWildcardMappingBuilder
 import net.corda.core.crypto.SecureHash
 import net.corda.core.crypto.newSecureRandom
 import net.corda.core.identity.CordaX500Name
@@ -307,7 +307,7 @@ internal fun createServerSNIOpenSslHandler(keyManagerFactoriesMap: Map<String, K
 
     // Default value can be any in the map.
     val sslCtxBuilder = getServerSslContextBuilder(keyManagerFactoriesMap.values.first(), trustManagerFactory)
-    val mapping = DomainNameMappingBuilder(sslCtxBuilder.build())
+    val mapping = DomainWildcardMappingBuilder(sslCtxBuilder.build())
     keyManagerFactoriesMap.forEach {
         mapping.add(it.key, sslCtxBuilder.keyManager(it.value).build())
     }
```
