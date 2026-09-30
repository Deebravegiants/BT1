# [?] [BESU-507] Resolve crashing NAT detectors on GKE (#731)

## Summary
Severity: Unknown
Chain: Ethereum
Component: hyperledger/besu
Published: 2020-04-17
Source: https://github.com/besu-eth/besu/commit/d7a65c0eba0eef56ea28a75fa8f55ba616d40129
Type: security-commit

## Details
[BESU-507] Resolve crashing NAT detectors on GKE (#731)

Resolve the NatManager crash when besu is launched on GKE and improved logs when switching to the fallback mode. It is no longer necessary in KUBERNETES to create a volume and to move the kubeconfig file in this volume.
Signed-off-by: Karim TAAM karim.t2am@gmail.com

## Patch
### nat/src/main/java/org/hyperledger/besu/nat/NatService.java
```diff
@@ -129,10 +129,10 @@ public String queryExternalIPAddress(final String fallbackValue) {
             .orElseThrow();
 
       } catch (Exception e) {
+        LOG.debug("Caught exception while trying to query NAT external IP address (ignoring)", e);
         LOG.warn(
-            "Caught exception while trying to query NAT external IP address (ignoring). Using the fallback value : {} ",
-            fallbackValue,
-            e);
+            "Unable to query NAT external IP address. Using the fallback value : {} ",
+            fallbackValue);
       }
     }
     return fallbackValue;
@@ -155,10 +155,9 @@ public String queryLocalIPAddress(final String fallbackValue) throws RuntimeExce
                 natManager.queryLocalIPAddress().get(NatManager.TIMEOUT_SECONDS, TimeUnit.SECONDS))
             .orElseThrow();
       } catch (Exception e) {
+        LOG.debug("Caught exception while trying to query NAT local IP address (ignoring)", e);
         LOG.warn(
-            "Caught exception while trying to query local IP address (ignoring). Using the fallback value : {} ",
-            fallbackValue,
-            e);
+            "Unable to query NAT local IP address. Using the fallback value : {} ", fallbackValue);
       }
     }
     return fallbackValue;
```

### nat/src/main/java/org/hyperledger/besu/nat/kubernetes/KubernetesNatManager.java
```diff
@@ -22,22 +22,21 @@
 import org.hyperledger.besu.nat.core.domain.NetworkProtocol;
 import org.hyperledger.besu.nat.core.exception.NatInitializationException;
 
-import java.nio.charset.Charset;
-import java.nio.file.Files;
-import java.nio.file.Paths;
+import java.net.InetAddress;
 import java.util.ArrayList;
 import java.util.List;
-import java.util.Optional;
 import java.util.concurrent.CompletableFuture;
 import java.util.concurrent.TimeUnit;
 
 import com.google.common.annotations.VisibleForTesting;
 import io.kubernetes.client.ApiClient;
 import io.kubernetes.client.Configuration;
 import io.kubernetes.client.apis.CoreV1Api;
+import io.kubernetes.client.models.V1LoadBalancerIngress;
 import io.kubernetes.client.models.V1Service;
 import io.kubernetes.client.util.ClientBuilder;
 import io.kubernetes.client.util.KubeConfig;
+import io.kubernetes.client.util.authenticators.GCPAuthenticator;
 import org.apache.logging.log4j.LogManager;
 import org.apache.logging.log4j.Logger;
 
@@ -48,8 +47,6 @@
 public class KubernetesNatManager extends AbstractNatManager {
   protected static final Logger LOG = LogManager.getLogger();
 
-  private static final String KUBE_CONFIG_PATH_ENV = "KUBE_CONFIG_PATH";
-  private static final String DEFAULT_KUBE_CONFIG_PATH = "~/.kube/config";
   private static final String DEFAULT_BESU_POD_NAME_FILTER = "besu";
 
   private String internalAdvertisedHost;
@@ -63,34 +60,27 @@ public KubernetesNatManager() {
   protected void doStart() throws NatInitializationException {
     LOG.info("Starting kubernetes NAT manager.");
     try {
+
+      KubeConfig.registerAuthenticator(new GCPAuthenticator());
+
       LOG.debug("Trying to update information using Kubernetes client SDK.");
-      final String kubeConfigPath =
-          Optional.ofNullable(System.getenv(KUBE_CONFIG_PATH_ENV)).orElse(DEFAULT_KUBE_CONFIG_PATH);
-      LOG.debug(
-          "Checking if Kubernetes config file is present on file system: {}.", kubeConfigPath);
-      if (!Files.exists(Paths.get(kubeConfigPath))) {
-        throw new NatInitializationException("Cannot locate Kubernetes config file.");
-      }
-      // loading the out-of-cluster config, a kubeconfig from file-system
-      final ApiClient client =
-          ClientBuilder.kubeconfig(
-                  KubeConfig.loadKubeConfig(
-                      Files.newBufferedReader(Paths.get(kubeConfigPath), Charset.defaultCharset())))
-              .build();
+      final ApiClient client = ClientBuilder.cluster().build();
 
       // set the global default api-client to the in-cluster one from above
       Configuration.setDefaultApiClient(client);
 
       // the CoreV1Api loads default api-client from global configuration.
-      CoreV1Api api = new CoreV1Api();
+      final CoreV1Api api = new CoreV1Api();
       // invokes the CoreV1Api client
-      api.listServiceForAllNamespaces(null, null, null, null, null, null, null, null, null)
-          .getItems().stream()
-          .filter(
-              v1Service -> v1Service.getMetadata().getName().contains(DEFAULT_BESU_POD_NAME_FILTER))
-          .findFirst()
-          .ifPresent(this::updateUsingBesuService);
-
+      final V1Service service =
+          api.listServiceForAllNamespaces(null, null, null, null, null, null, null, null, null)
+              .getItems().stream()
+              .filter(
+                  v1Service ->
+                      v1Service.getMetadata().getName().contains(DEFAULT_BESU_POD_NAME_FILTER))
+              .findFirst()
+              .orElseThrow(() -> new NatInitializationException("Service not found"));
+      updateUsingBesuService(service);
     } catch (Exception e) {
       throw new NatInitializationException(
           "Failed update information using Kubernetes client SDK.", e);
@@ -101,8 +91,25 @@ protected void doStart() throws NatInitializationException {
   void updateUsingBesuService(final V1Service service) throws RuntimeException {
     try {
       LOG.info("Found Besu service: {}", service.getMetadata().getName());
-      LOG.info("Setting host IP to: {}.", service.getSpec().getClusterIP());
-      internalAdvertisedHost = service.getSpec().getClusterIP();
+
+      final V1LoadBalancerIngress v1LoadBalancerIngress =
+          service.getStatus().getLoadBalancer().getIngress().stream()
+              .filter(
+                  v1LoadBalancerIngress1 ->
+                      v1LoadBalancerIngress1.getHostname() != null
+                          || v1LoadBalancerIngress1.getIp() != null)
+              .findFirst()
+              .orElseThrow(() -> new NatInitializationException("Ingress not found"));
+
+      if (v1LoadBalancerIngress.getHostname() != null) {
+        internalAdvertisedHost =
+            InetAddress.getByName(v1LoadBalancerIngress.getHostname()).getHostAddress();
+      } else {
+        internalAdvertisedHost = v1LoadBalancerIngress.getIp();
+      }
+
+      LOG.info("Setting host IP to: {}.", internalAdvertisedHost);
+
       final String internalHost = queryLocalIPAddress().get(TIMEOUT_SECONDS, TimeUnit.SECONDS);
       service
           .getSpec()
```

### nat/src/test/java/org/hyperledger/besu/nat/kubernetes/KubernetesNatManagerTest.java
```diff
@@ -28,10 +28,13 @@
 import java.util.concurrent.ExecutionException;
 
 import io.kubernetes.client.custom.IntOrString;
+import io.kubernetes.client.models.V1LoadBalancerIngressBuilder;
+import io.kubernetes.client.models.V1LoadBalancerStatusBuilder;
 import io.kubernetes.client.models.V1ObjectMeta;
 import io.kubernetes.client.models.V1Service;
 import io.kubernetes.client.models.V1ServicePort;
 import io.kubernetes.client.models.V1ServiceSpec;
+import io.kubernetes.client.models.V1ServiceStatus;
 import org.junit.Before;
 import org.junit.Test;
 import org.junit.runner.RunWith;
@@ -52,10 +55,17 @@ public final class KubernetesNatManagerTest {
 
   @Before
   public void initialize() throws IOException {
+    final V1ServiceStatus v1ServiceStatus =
+        new V1ServiceStatus()
+            .loadBalancer(
+                new V1LoadBalancerStatusBuilder()
+                    .addToIngress(
+                        new V1LoadBalancerIngressBuilder().withIp(detectedAdvertisedHost).build())
+                    .build());
+    when(v1Service.getStatus()).thenReturn(v1ServiceStatus);
     when(v1Service.getSpec())
         .thenReturn(
             new V1ServiceSpec()
-                .clusterIP(detectedAdvertisedHost)
                 .ports(
                     Arrays.asList(
                         new V1ServicePort()
```
