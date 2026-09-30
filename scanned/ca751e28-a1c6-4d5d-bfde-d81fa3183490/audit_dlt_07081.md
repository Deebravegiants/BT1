# [?] Fixes: GHSA-f429-4669-7rpx fix(auth): fail when ephemeral Engine API JWT key cannot be persisted (#115)

## Summary
Severity: Unknown
Chain: Ethereum
Component: hyperledger/besu
Published: 2026-08-28
Source: https://github.com/besu-eth/besu/commit/90028d364996c5807ad69e8a4f1af43039114f7e
Type: security-commit

## Details
Fixes: GHSA-f429-4669-7rpx fix(auth): fail when ephemeral Engine API JWT key cannot be persisted (#115)

* fix(auth): fail closed when ephemeral Engine API JWT key cannot be persisted

When Files.writeString raised IOException writing jwt.hex, the previous
code logged the raw signing secret at INFO and continued starting up.
Any reader of the application log could recover the key and obtain full
Engine API access.

Replace the warn+continue path with UnsecurableEngineApiException,
matching the existing fail-closed behaviour for operator-configured key
file failures. The error message directs operators to --engine-jwt-secret
as the supported path for read-only data directories.

Fixes: GHSA-f429-4669-7rpx
Closes #91

---------

Signed-off-by: Sally MacFarlane <sally.macfarlane@consensys.net>
Signed-off-by: Sally MacFarlane <macfarla.github@gmail.com>
Co-authored-by: Justin Florentine <justin+github@florentine.us>
Signed-off-by: Sally MacFarlane <macfarla.github@gmail.com>

## Patch
### app/src/test/java/org/hyperledger/besu/RunnerBuilderTest.java
```diff
@@ -169,7 +169,7 @@ public void enodeUrlShouldHaveAdvertisedHostWhenDiscoveryDisabled() {
             .inProcessRpcConfiguration(mock(InProcessRpcConfiguration.class))
             .metricsConfiguration(mock(MetricsConfiguration.class))
             .vertx(vertx)
-            .dataDir(dataDir.getRoot())
+            .dataDir(dataDir)
             .storageProvider(mock(KeyValueStorageProvider.class, RETURNS_DEEP_STUBS))
             .rpcEndpointService(new RpcEndpointServiceImpl())
             .apiConfiguration(ImmutableApiConfiguration.builder().build())
@@ -221,7 +221,7 @@ public void movingAcrossProtocolSpecsUpdatesNodeRecord() {
             .inProcessRpcConfiguration(mock(InProcessRpcConfiguration.class))
             .metricsConfiguration(mock(MetricsConfiguration.class))
             .vertx(Vertx.vertx())
-            .dataDir(dataDir.getRoot())
+            .dataDir(dataDir)
             .storageProvider(storageProvider)
             .rpcEndpointService(new RpcEndpointServiceImpl())
             .apiConfiguration(ImmutableApiConfiguration.builder().build())
@@ -390,7 +390,7 @@ public void whenEngineApiAddedListensOnDefaultPort() {
             .inProcessRpcConfiguration(mock(InProcessRpcConfiguration.class))
             .metricsConfiguration(mock(MetricsConfiguration.class))
             .vertx(Vertx.vertx())
-            .dataDir(dataDir.getRoot())
+            .dataDir(dataDir)
             .storageProvider(mock(KeyValueStorageProvider.class, RETURNS_DEEP_STUBS))
             .rpcEndpointService(new RpcEndpointServiceImpl())
             .besuPluginContext(mock(BesuPluginContextImpl.class))
@@ -435,7 +435,7 @@ public void whenEngineApiAddedWebSocketReadyOnSamePort() {
             .graphQLConfiguration(mock(GraphQLConfiguration.class))
             .metricsConfiguration(mock(MetricsConfiguration.class))
             .vertx(Vertx.vertx())
-            .dataDir(dataDir.getRoot())
+            .dataDir(dataDir)
             .storageProvider(mock(KeyValueStorageProvider.class, RETURNS_DEEP_STUBS))
             .rpcEndpointService(new RpcEndpointServiceImpl())
             .besuPluginContext(mock(BesuPluginContextImpl.class))
@@ -479,7 +479,7 @@ public void whenEngineApiAddedEthSubscribeAvailable() {
             .graphQLConfiguration(mock(GraphQLConfiguration.class))
             .metricsConfiguration(mock(MetricsConfiguration.class))
             .vertx(Vertx.vertx())
-            .dataDir(dataDir.getRoot())
+            .dataDir(dataDir)
             .storageProvider(mock(KeyValueStorageProvider.class, RETURNS_DEEP_STUBS))
             .rpcEndpointService(new RpcEndpointServiceImpl())
             .besuPluginContext(mock(BesuPluginContextImpl.class))
@@ -524,7 +524,7 @@ public void noEngineApiNoServiceForMethods() {
             .inProcessRpcConfiguration(mock(InProcessRpcConfiguration.class))
             .metricsConfiguration(mock(MetricsConfiguration.class))
             .vertx(Vertx.vertx())
-            .dataDir(dataDir.getRoot())
+            .dataDir(dataDir)
             .storageProvider(mock(KeyValueStorageProvider.class, RETURNS_DEEP_STUBS))
             .rpcEndpointService(new RpcEndpointServiceImpl())
             .besuPluginContext(mock(BesuPluginContextImpl.class))
```

### ethereum/api/src/main/java/org/hyperledger/besu/ethereum/api/jsonrpc/authentication/EngineAuthService.java
```diff
@@ -86,15 +86,21 @@ public String createToken() {
   private JWTAuthOptions engineApiJWTOptions(
       final JwtAlgorithm jwtAlgorithm, final Optional<File> keyFile, final Path datadir) {
     byte[] signingKey = null;
-    if (!keyFile.isPresent()) {
+    if (keyFile.isEmpty()) {
       final File jwtFile = new File(datadir.toFile(), EPHEMERAL_JWT_FILE);
       jwtFile.deleteOnExit();
       final byte[] ephemeralKey = Bytes32.random().toArray();
       try {
         Files.writeString(jwtFile.toPath(), Codec.base16Encode(ephemeralKey));
       } catch (IOException ioe) {
-        LOG.warn("Unable to write ephemeral jwt key file to {}", jwtFile.toPath().toString());
-        LOG.info("JWT KEY: {}", Codec.base16Encode(ephemeralKey));
+        UnsecurableEngineApiException e =
+            new UnsecurableEngineApiException(
+                "Unable to write ephemeral JWT key to "
+                    + jwtFile.toPath()
+                    + "; use --engine-jwt-secret to supply a key file in a writable location");
+        e.fillInStackTrace();
+        e.initCause(ioe);
+        throw e;
       }
       signingKey = ephemeralKey;
     } else { // user configured option to use a specified file
```

### ethereum/api/src/test/java/org/hyperledger/besu/ethereum/api/jsonrpc/authentication/EngineAuthServiceTest.java
```diff
@@ -75,6 +75,18 @@ public void handle(final Optional<User> event) {
     auth.authenticate(token, authHandler);
   }
 
+  @Test
+  public void throwsWhenEphemeralKeyCannotBePersisted() throws IOException {
+    Vertx vertx = mock(Vertx.class);
+    // Deliberately make jwt.hex a directory so Files.writeString raises IOException.
+    Path dataDir = Files.createTempDirectory("besuUnitTest");
+    dataDir.resolve(EngineAuthService.EPHEMERAL_JWT_FILE).toFile().mkdir();
+
+    assertThatThrownBy(() -> new EngineAuthService(vertx, Optional.empty(), dataDir))
+        .isInstanceOf(UnsecurableEngineApiException.class)
+        .hasMessageContaining("--engine-jwt-secret");
+  }
+
   @Test
   public void throwsOnShortKey() throws IOException, URISyntaxException {
     Vertx vertx = mock(Vertx.class);
```
