# [?] [CORDA-1638]: Node crashes in --initial-registration polling mode if doorman returns a transient HTTP error (fix). (#3403)

## Summary
Severity: Unknown
Chain: Corda
Component: corda/corda
Published: 2018-06-19
Source: https://github.com/corda/corda/commit/af93ff8d1c44518a8effad2c3d0e45926a3dcfc7
Type: security-commit

## Details
[CORDA-1638]: Node crashes in --initial-registration polling mode if doorman returns a transient HTTP error (fix). (#3403)

## Patch
### docs/source/changelog.rst
```diff
@@ -7,6 +7,9 @@ release, see :doc:`upgrade-notes`.
 Unreleased
 ==========
 
+* Introduced a grace period before the initial node registration fails if the node cannot connect to the Doorman.
+  It retries 10 times with a 1 minute interval in between each try. At the moment this is not configurable.
+
 * Added a ``FlowMonitor`` to log information about flows that have been waiting for IO more than a configurable threshold.
 
 * H2 database changes:
```

### node/src/main/kotlin/net/corda/node/internal/NodeStartup.kt
```diff
@@ -25,6 +25,7 @@ import net.corda.node.services.config.shouldStartSSHDaemon
 import net.corda.node.services.transactions.bftSMaRtSerialFilter
 import net.corda.node.utilities.registration.HTTPNetworkRegistrationService
 import net.corda.node.utilities.registration.NodeRegistrationHelper
+import net.corda.node.utilities.registration.UnableToRegisterNodeWithDoormanException
 import net.corda.nodeapi.internal.addShutdownHook
 import net.corda.nodeapi.internal.config.UnknownConfigurationKeysException
 import net.corda.nodeapi.internal.persistence.CouldNotCreateDataSourceException
@@ -121,6 +122,9 @@ open class NodeStartup(val args: Array<String>) {
                 return true
             }
             logStartupInfo(versionInfo, cmdlineOptions, conf)
+        } catch (e: UnableToRegisterNodeWithDoormanException) {
+            logger.warn("Node registration service is unavailable. Perhaps try to perform the initial registration again after a while.")
+            return false
         } catch (e: Exception) {
             logger.error("Exception during node registration", e)
             return false
```

### node/src/main/kotlin/net/corda/node/utilities/registration/HTTPNetworkRegistrationService.kt
```diff
@@ -16,13 +16,15 @@ import java.net.URL
 import java.security.cert.X509Certificate
 import java.util.*
 import java.util.zip.ZipInputStream
+import javax.naming.ServiceUnavailableException
 
 class HTTPNetworkRegistrationService(compatibilityZoneURL: URL) : NetworkRegistrationService {
     private val registrationURL = URL("$compatibilityZoneURL/certificate")
 
     companion object {
         // TODO: Propagate version information from gradle
         const val CLIENT_VERSION = "1.0"
+        private val TRANSIENT_ERROR_STATUS_CODES = setOf(HTTP_BAD_GATEWAY, HTTP_UNAVAILABLE, HTTP_GATEWAY_TIMEOUT)
     }
 
     @Throws(CertificateRequestException::class)
@@ -45,7 +47,8 @@ class HTTPNetworkRegistrationService(compatibilityZoneURL: URL) : NetworkRegistr
             }
             HTTP_NO_CONTENT -> CertificateResponse(pollInterval, null)
             HTTP_UNAUTHORIZED -> throw CertificateRequestException("Certificate signing request has been rejected: ${conn.errorMessage}")
-            else -> throw IOException("Response Code ${conn.responseCode}: ${conn.errorMessage}")
+            in TRANSIENT_ERROR_STATUS_CODES -> throw ServiceUnavailableException("Could not connect with Doorman. Http response status code was ${conn.responseCode}.")
+            else -> throw IOException("Error while connecting to the Doorman. Http response status code was ${conn.responseCode}.")
         }
     }
 
```

### node/src/main/kotlin/net/corda/node/utilities/registration/NetworkRegistrationHelper.kt
```diff
@@ -16,12 +16,15 @@ import net.corda.nodeapi.internal.crypto.X509Utilities.CORDA_ROOT_CA
 import org.bouncycastle.asn1.x500.X500Name
 import org.bouncycastle.openssl.jcajce.JcaPEMWriter
 import org.bouncycastle.util.io.pem.PemObject
+import java.io.IOException
 import java.io.StringWriter
 import java.nio.file.Path
 import java.security.KeyPair
 import java.security.KeyStore
 import java.security.PublicKey
 import java.security.cert.X509Certificate
+import java.time.Duration
+import javax.naming.ServiceUnavailableException
 
 /**
  * Helper for managing the node registration process, which checks for any existing certificates and requests them if
@@ -35,7 +38,8 @@ open class NetworkRegistrationHelper(private val config: SSLConfiguration,
                                      private val networkRootTrustStorePath: Path,
                                      networkRootTrustStorePassword: String,
                                      private val keyAlias: String,
-                                     private val certRole: CertRole) {
+                                     private val certRole: CertRole,
+                                     private val nextIdleDuration: (Duration?) -> Duration? = FixedPeriodLimitedRetrialStrategy(10, Duration.ofMinutes(1))) {
 
     companion object {
         const val SELF_SIGNED_PRIVATE_KEY = "Self Signed Private Key"
@@ -160,12 +164,22 @@ open class NetworkRegistrationHelper(private val config: SSLConfiguration,
     private fun pollServerForCertificates(requestId: String): List<X509Certificate> {
         println("Start polling server for certificate signing approval.")
         // Poll server to download the signed certificate once request has been approved.
+        var idlePeriodDuration: Duration? = null
         while (true) {
-            val (pollInterval, certificates) = certService.retrieveCertificates(requestId)
-            if (certificates != null) {
-                return certificates
+            try {
+                val (pollInterval, certificates) = certService.retrieveCertificates(requestId)
+                if (certificates != null) {
+                    return certificates
+                }
+                Thread.sleep(pollInterval.toMillis())
+            } catch (e: ServiceUnavailableException) {
+                idlePeriodDuration = nextIdleDuration(idlePeriodDuration)
+                if (idlePeriodDuration != null) {
+                    Thread.sleep(idlePeriodDuration.toMillis())
+                } else {
+                    throw UnableToRegisterNodeWithDoormanException()
+                }
             }
-            Thread.sleep(pollInterval.toMillis())
         }
     }
 
@@ -208,15 +222,18 @@ open class NetworkRegistrationHelper(private val config: SSLConfiguration,
     protected open fun onSuccess(nodeCAKeyPair: KeyPair, certificates: List<X509Certificate>) {}
 }
 
-class NodeRegistrationHelper(private val config: NodeConfiguration, certService: NetworkRegistrationService, regConfig: NodeRegistrationOption) :
+class UnableToRegisterNodeWithDoormanException : IOException()
+
+class NodeRegistrationHelper(private val config: NodeConfiguration, certService: NetworkRegistrationService, regConfig: NodeRegistrationOption, computeNextIdleDoormanConnectionPollInterval: (Duration?) -> Duration? = FixedPeriodLimitedRetrialStrategy(10, Duration.ofMinutes(1))) :
         NetworkRegistrationHelper(config,
                 config.myLegalName,
                 config.emailAddress,
                 certService,
                 regConfig.networkRootTrustStorePath,
                 regConfig.networkRootTrustStorePassword,
                 CORDA_CLIENT_CA,
-                CertRole.NODE_CA) {
+                CertRole.NODE_CA,
+                computeNextIdleDoormanConnectionPollInterval) {
 
     companion object {
         val logger = contextLogger()
@@ -255,3 +272,18 @@ class NodeRegistrationHelper(private val config: NodeConfiguration, certService:
         println("Node trust store stored in ${config.trustStoreFile}.")
     }
 }
+
+private class FixedPeriodLimitedRetrialStrategy(times: Int, private val period: Duration) : (Duration?) -> Duration? {
+
+    init {
+        require(times > 0)
+    }
+
+    private var counter = times
+
+    override fun invoke(@Suppress("UNUSED_PARAMETER") previousPeriod: Duration?): Duration? {
+        synchronized(this) {
+            return if (counter-- > 0) period else null
+        }
+    }
+}
\ No newline at end of file
```
