# [?] fix: [main CP 10/12] cherry-pick to main: non-deterministic gossip CA certificate validation (#26424)

## Summary
Severity: Unknown
Chain: Hedera
Component: hiero-ledger/hiero-consensus-node
Published: 2026-07-20
Source: https://github.com/hiero-ledger/hiero-consensus-node/commit/0460f384ddc3aaa9c66ece29b0e9ac39f19367c5
Type: security-commit

## Details
fix: [main CP 10/12] cherry-pick to main: non-deterministic gossip CA certificate validation (#26424)

Signed-off-by: Akram AbouEmara <508522+akdev@users.noreply.github.com>
Co-authored-by: aderevets <artem.derevets@limechain.tech>
Co-authored-by: Neeharika Sompalli <52669918+Neeharika-Sompalli@users.noreply.github.com>

## Patch
### hedera-node/hedera-addressbook-service-impl/src/main/java/com/hedera/node/app/service/addressbook/impl/handlers/NodeCreateHandler.java
```diff
@@ -9,6 +9,7 @@
 import static com.hedera.hapi.node.base.ResponseCodeEnum.INVALID_SERVICE_ENDPOINT;
 import static com.hedera.hapi.node.base.ResponseCodeEnum.INVALID_SIGNATURE;
 import static com.hedera.hapi.node.base.ResponseCodeEnum.MAX_NODES_CREATED;
+import static com.hedera.node.app.service.addressbook.impl.validators.AddressBookValidator.parseX509Certificate;
 import static com.hedera.node.app.service.addressbook.impl.validators.AddressBookValidator.validateX509Certificate;
 import static com.hedera.node.app.spi.workflows.HandleContext.DispatchMetadata.Type.SYSTEM_TXN_CREATION_ENTITY_NUM;
 import static com.hedera.node.app.spi.workflows.HandleException.validateTrue;
@@ -68,7 +69,7 @@ public void pureChecks(@NonNull final PureChecksContext context) throws PreCheck
                 op.gossipCaCertificate().length() == 0
                         || op.gossipCaCertificate().equals(Bytes.EMPTY),
                 INVALID_GOSSIP_CA_CERTIFICATE);
-        validateX509Certificate(op.gossipCaCertificate());
+        parseX509Certificate(op.gossipCaCertificate());
         final var adminKey = op.adminKey();
         addressBookValidator.validateAdminKey(adminKey);
     }
@@ -110,6 +111,9 @@ public void handle(@NonNull final HandleContext handleContext) {
         addressBookValidator.validateDescription(op.description(), nodeConfig);
         addressBookValidator.validateGossipEndpoint(op.gossipEndpoint(), nodeConfig);
         addressBookValidator.validateServiceEndpoint(op.serviceEndpoint(), nodeConfig);
+        if (!op.gossipCaCertificate().equals(Bytes.EMPTY)) {
+            validateX509Certificate(op.gossipCaCertificate(), handleContext.consensusNow());
+        }
         if (op.hasGrpcProxyEndpoint()) {
             validateTrue(nodeConfig.webProxyEndpointsEnabled(), GRPC_WEB_PROXY_NOT_SUPPORTED);
             addressBookValidator.validateFqdnEndpoint(op.grpcProxyEndpoint(), nodeConfig);
```

### hedera-node/hedera-addressbook-service-impl/src/main/java/com/hedera/node/app/service/addressbook/impl/handlers/NodeUpdateHandler.java
```diff
@@ -10,6 +10,7 @@
 import static com.hedera.hapi.node.base.ResponseCodeEnum.INVALID_SIGNATURE;
 import static com.hedera.hapi.node.base.ResponseCodeEnum.NODE_ACCOUNT_HAS_ZERO_BALANCE;
 import static com.hedera.hapi.node.base.ResponseCodeEnum.UPDATE_NODE_ACCOUNT_NOT_ALLOWED;
+import static com.hedera.node.app.service.addressbook.impl.validators.AddressBookValidator.parseX509Certificate;
 import static com.hedera.node.app.service.addressbook.impl.validators.AddressBookValidator.validateX509Certificate;
 import static com.hedera.node.app.spi.workflows.HandleException.validateFalse;
 import static com.hedera.node.app.spi.workflows.HandleException.validateTrue;
@@ -68,7 +69,7 @@ public void pureChecks(@NonNull final PureChecksContext context) throws PreCheck
         validateFalsePreCheck(op.nodeId() < 0, INVALID_NODE_ID);
         if (op.hasGossipCaCertificate()) {
             validateFalsePreCheck(op.gossipCaCertificate().equals(Bytes.EMPTY), INVALID_GOSSIP_CA_CERTIFICATE);
-            validateX509Certificate(op.gossipCaCertificate());
+            parseX509Certificate(op.gossipCaCertificate());
         }
         if (op.hasAdminKey()) {
             final var adminKey = op.adminKey();
@@ -126,6 +127,9 @@ public void handle(@NonNull final HandleContext handleContext) {
 
         final var existingNode = nodeStore.get(op.nodeId());
         validateFalse(existingNode == null, INVALID_NODE_ID);
+        if (op.hasGossipCaCertificate()) {
+            validateX509Certificate(op.gossipCaCertificateOrThrow(), handleContext.consensusNow());
+        }
         if (op.hasAccountId()) {
             final var accountId = op.accountIdOrThrow();
             validateTrue(accountStore.contains(accountId), INVALID_NODE_ACCOUNT_ID);
```

### hedera-node/hedera-addressbook-service-impl/src/main/java/com/hedera/node/app/service/addressbook/impl/validators/AddressBookValidator.java
```diff
@@ -54,6 +54,9 @@
 import java.io.ByteArrayInputStream;
 import java.io.ByteArrayOutputStream;
 import java.nio.charset.StandardCharsets;
+import java.security.cert.X509Certificate;
+import java.time.Instant;
+import java.util.Date;
 import java.util.List;
 import javax.inject.Inject;
 import javax.inject.Singleton;
@@ -240,26 +243,43 @@ private void validateFqdnSize(@NonNull final ServiceEndpoint endpoint, @NonNull
     }
 
     /**
-     * Validates the given bytes encode an X509 certificate can be serialized and deserialized from
-     * PEM format to recover a usable certificate.
-     * @param x509CertBytes the bytes to validate
-     * @throws PreCheckException if the certificate is invalid
+     * Parses the given bytes as an X509 certificate after serializing and deserializing from PEM format.
+     * @param x509CertBytes the bytes to parse
+     * @return the parsed certificate
+     * @throws PreCheckException if the certificate cannot be parsed
      */
-    public static void validateX509Certificate(@NonNull final Bytes x509CertBytes) throws PreCheckException {
+    public static X509Certificate parseX509Certificate(@NonNull final Bytes x509CertBytes) throws PreCheckException {
         try {
-            // Serialize the given bytes to a PEM file just as we would on a PREPARE_UPGRADE
-            final var baos = new ByteArrayOutputStream();
-            writeCertificatePemFile(x509CertBytes.toByteArray(), baos);
-            // Deserialize an X509 certificate from the resulting PEM file
-            final var bais = new ByteArrayInputStream(baos.toByteArray());
-            final var cert = readCertificatePemFile(bais);
-            // And check its validity for completeness
-            cert.checkValidity();
+            return parseX509CertificateOrThrow(x509CertBytes);
         } catch (Exception ignore) {
             throw new PreCheckException(INVALID_GOSSIP_CA_CERTIFICATE);
         }
     }
 
+    /**
+     * Validates the given bytes encode an X509 certificate that is usable at the given deterministic time.
+     * @param x509CertBytes the bytes to validate
+     * @param validAt the consensus time to use for certificate validity checks
+     * @throws HandleException if the certificate is invalid
+     */
+    public static void validateX509Certificate(@NonNull final Bytes x509CertBytes, @NonNull final Instant validAt) {
+        requireNonNull(validAt, "validAt must not be null");
+        try {
+            parseX509CertificateOrThrow(x509CertBytes).checkValidity(Date.from(validAt));
+        } catch (Exception ignore) {
+            throw new HandleException(INVALID_GOSSIP_CA_CERTIFICATE);
+        }
+    }
+
+    private static X509Certificate parseX509CertificateOrThrow(@NonNull final Bytes x509CertBytes) throws Exception {
+        // Serialize the given bytes to a PEM file just as we would on a PREPARE_UPGRADE
+        final var baos = new ByteArrayOutputStream();
+        writeCertificatePemFile(x509CertBytes.toByteArray(), baos);
+        // Deserialize an X509 certificate from the resulting PEM file
+        final var bais = new ByteArrayInputStream(baos.toByteArray());
+        return readCertificatePemFile(bais);
+    }
+
     /**
      * Validates registered service endpoints for a create operation. The list must be non-empty
      * and contain at most nodesConfig.maxRegisteredServiceEndpoint entries.
```

### hedera-node/hedera-addressbook-service-impl/src/test/java/com/hedera/node/app/service/addressbook/impl/test/CertificatePemTest.java
```diff
@@ -5,7 +5,7 @@
 import static com.hedera.node.app.service.addressbook.AddressBookHelper.loadResourceFile;
 import static com.hedera.node.app.service.addressbook.AddressBookHelper.readCertificatePemFile;
 import static com.hedera.node.app.service.addressbook.AddressBookHelper.writeCertificatePemFile;
-import static com.hedera.node.app.service.addressbook.impl.validators.AddressBookValidator.validateX509Certificate;
+import static com.hedera.node.app.service.addressbook.impl.validators.AddressBookValidator.parseX509Certificate;
 import static org.assertj.core.api.AssertionsForClassTypes.assertThat;
 import static org.junit.jupiter.api.Assertions.assertArrayEquals;
 import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
@@ -45,7 +45,7 @@ void validateGeneratedPemFile() throws IOException, CertificateException {
         assertEquals("X.509", cert.getType());
         assertArrayEquals(cert.getEncoded(), genCert.getEncoded());
         assertEquals(cert, genCert);
-        assertDoesNotThrow(() -> validateX509Certificate(Bytes.wrap(genCert.getEncoded())));
+        assertDoesNotThrow(() -> parseX509Certificate(Bytes.wrap(genCert.getEncoded())));
     }
 
     @Test
@@ -72,7 +72,7 @@ void invalidBytesInPemCannotRead() throws IOException {
         writeCertificatePemFile(genPemPath, Bytes.wrap("anyString").toByteArray());
         final var exception = assertThrows(IOException.class, () -> readCertificatePemFile(genPemPath));
         assertThat(exception.getMessage()).contains("problem parsing cert: java.io.EOFException:");
-        final var msg = assertThrows(PreCheckException.class, () -> validateX509Certificate(Bytes.wrap("anyString")));
+        final var msg = assertThrows(PreCheckException.class, () -> parseX509Certificate(Bytes.wrap("anyString")));
         assertEquals(ResponseCodeEnum.INVALID_GOSSIP_CA_CERTIFICATE, msg.responseCode());
     }
 
@@ -84,7 +84,7 @@ void badX509CertificateFailedOnReadAndValidation() throws IOException {
         assertEquals("problem parsing cert: java.io.IOException: unknown tag 13 encountered", exception.getMessage());
 
         final byte[] certBytes = Files.readAllBytes(pemFilePath);
-        final var msg = assertThrows(PreCheckException.class, () -> validateX509Certificate(Bytes.wrap(certBytes)));
+        final var msg = assertThrows(PreCheckException.class, () -> parseX509Certificate(Bytes.wrap(certBytes)));
         assertEquals(ResponseCodeEnum.INVALID_GOSSIP_CA_CERTIFICATE, msg.responseCode());
         final var getmsg = assertThrows(PreCheckException.class, () -> getX509Certificate(Bytes.wrap(certBytes)));
         assertEquals(ResponseCodeEnum.INVALID_GOSSIP_CA_CERTIFICATE, getmsg.responseCode());
@@ -99,7 +99,7 @@ void goodX509CertificateSuccessOnReadAndValidation() throws IOException, Certifi
         assertEquals("SHA384withRSA", cert.getSigAlgName());
         assertEquals("X.509", cert.getType());
         assertDoesNotThrow(() -> getX509Certificate(Bytes.wrap(cert.getEncoded())));
-        assertDoesNotThrow(() -> validateX509Certificate(Bytes.wrap(cert.getEncoded())));
+        assertDoesNotThrow(() -> parseX509Certificate(Bytes.wrap(cert.getEncoded())));
 
         final byte[] certBytes = Files.readAllBytes(pemFilePath);
         assertDoesNotThrow(() -> getX509Certificate(Bytes.wrap(certBytes)));
```

### hedera-node/hedera-addressbook-service-impl/src/test/java/com/hedera/node/app/service/addressbook/impl/test/handlers/NodeCreateHandlerTest.java
```diff
@@ -55,6 +55,7 @@
 import com.swirlds.config.api.Configuration;
 import java.security.cert.CertificateEncodingException;
 import java.security.cert.X509Certificate;
+import java.time.Instant;
 import java.util.List;
 import org.junit.jupiter.api.BeforeAll;
 import org.junit.jupiter.api.BeforeEach;
@@ -88,6 +89,7 @@ class NodeCreateHandlerTest extends AddressBookTestBase {
     private TransactionBody txn;
     private NodeCreateHandler subject;
 
+    private static final Instant VALID_CERT_TIME = Instant.parse("2010-01-01T00:00:00Z");
     private static List<X509Certificate> certList;
 
     @BeforeAll
@@ -524,6 +526,27 @@ void handleFailsWhenInvalidAdminKey() {
         assertEquals(ResponseCodeEnum.INVALID_ADMIN_KEY, msg.getStatus());
     }
 
+    @Test
+    void handleFailsWhenGossipCaCertificateIsInvalid() {
+        txn = new NodeCreateBuilder()
+                .withAccountId(accountId)
+                .withDescription("Description")
+                .withGossipEndpoint(List.of(endpoint1, endpoint2))
+                .withServiceEndpoint(List.of(endpoint1, endpoint3))
+                .withGossipCaCertificate(Bytes.wrap("not a cert"))
+                .withAdminKey(key)
+                .build(payerId);
+        final var config = HederaTestConfigBuilder.create()
+                .withValue("nodes.nodeMaxDescriptionUtf8Bytes", 12)
+                .withValue("nodes.maxGossipEndpoint", 4)
+                .withValue("nodes.maxServiceEndpoint", 3)
+                .getOrCreateConfig();
+        setupHandle(config);
+
+        final var msg = assertThrows(HandleException.class, () -> subject.handle(handleContext));
+        assertEquals(INVALID_GOSSIP_CA_CERTIFICATE, msg.getStatus());
+    }
+
     @Test
     void handleWorksAsExpected() throws CertificateEncodingException {
         txn = new NodeCreateBuilder()
@@ -860,6 +883,7 @@ void handleWorksForSystemTxnWithExistingNode() throws CertificateEncodingExcepti
                 .getOrCreateConfig();
 
         given(handleContext.body()).willReturn(txn);
+        given(handleContext.consensusNow()).willReturn(VALID_CERT_TIME);
         given(handleContext.storeFactory()).willReturn(storeFactory);
         given(handleContext.configuration()).willReturn(config);
         given(handleContext.expiryValidator()).willReturn(expiryValidator);
@@ -916,6 +940,7 @@ void handleRemovesPreviousAccountRelationForSystemTxnWithExistingNode() throws C
                 .getOrCreateConfig();
 
         given(handleContext.body()).willReturn(txn);
+        given(handleContext.consensusNow()).willReturn(VALID_CERT_TIME);
         given(handleContext.storeFactory()).willReturn(storeFactory);
         given(handleContext.configuration()).willReturn(config);
         given(handleContext.expiryValidator()).willReturn(expiryValidator);
@@ -972,6 +997,7 @@ void handleFailsForSystemTxnWithRegisteredNodeCollision() throws CertificateEnco
                 .getOrCreateConfig();
 
         given(handleContext.body()).willReturn(txn);
+        given(handleContext.consensusNow()).willReturn(VALID_CERT_TIME);
         given(handleContext.storeFactory()).willReturn(storeFactory);
         given(handleContext.configuration()).willReturn(config);
         given(handleContext.expiryValidator()).willReturn(expiryValidator);
@@ -1039,6 +1065,7 @@ private void setupHandle() {
 
     private void setupHandle(Configuration config) {
         given(handleContext.body()).willReturn(txn);
+        given(handleContext.consensusNow()).willReturn(VALID_CERT_TIME);
         given(handleContext.storeFactory()).willReturn(storeFactory);
         given(handleContext.configuration()).willReturn(config);
         given(handleContext.storeFactory()).willReturn(storeFactory);
```

### hedera-node/hedera-addressbook-service-impl/src/test/java/com/hedera/node/app/service/addressbook/impl/test/handlers/NodeUpdateHandlerTest.java
```diff
@@ -58,7 +58,10 @@
 import com.hedera.pbj.runtime.io.buffer.Bytes;
 import com.swirlds.state.test.fixtures.MapWritableKVState;
 import java.security.cert.CertificateEncodingException;
+import java.security.cert.CertificateExpiredException;
 import java.security.cert.X509Certificate;
+import java.time.Instant;
+import java.util.Date;
 import java.util.List;
 import java.util.Optional;
 import org.junit.jupiter.api.BeforeAll;
@@ -93,6 +96,7 @@ class NodeUpdateHandlerTest extends AddressBookTestBase {
     private final AccountID newAccountId = idFactory.newAccountId(53);
     private TransactionBody txn;
     private NodeUpdateHandler subject;
+    private static final Instant VALID_CERT_TIME = Instant.parse("2010-01-01T00:00:00Z");
     private static List<X509Certificate> certList;
 
     @BeforeAll
@@ -167,9 +171,40 @@ void pureCheckPass() throws CertificateEncodingException {
         assertDoesNotThrow(() -> subject.pureChecks(pureChecksContext));
     }
 
+    @Test
+    @DisplayName("pureChecks fail when gossipCaCertificate cannot be parsed")
+    void pureChecksFailsWhenGossipCaCertificateCannotBeParsed() {
+        txn = new NodeUpdateBuilder()
+                .withNodeId(1)
+                .withGossipCaCertificate(Bytes.wrap("not a cert"))
+                .build();
+        given(pureChecksContext.body()).willReturn(txn);
+
+        final var msg = assertThrows(PreCheckException.class, () -> subject.pureChecks(pureChecksContext));
+        assertThat(msg.responseCode()).isEqualTo(INVALID_GOSSIP_CA_CERTIFICATE);
+    }
+
+    @Test
+    void pureChecksDoesNotValidateGossipCaCertificateExpiration() throws CertificateEncodingException {
+        final var cert = certList.getFirst();
+        txn = new NodeUpdateBuilder()
+                .withNodeId(1)
+                .withGossipCaCertificate(Bytes.wrap(cert.getEncoded()))
+                .build();
+        given(pureChecksContext.body()).willReturn(txn);
+
+        final var afterCertificateExpiry =
+                Date.from(cert.getNotAfter().toInstant().plusSeconds(1));
+        assertThrows(CertificateExpiredException.class, () -> cert.checkValidity(afterCertificateExpiry));
+        assertDoesNotThrow(() -> subject.pureChecks(pureChecksContext));
+    }
+
     @Test
     void nodeIdMustInState() {
-        txn = new NodeUpdateBuilder().withNodeId(2L).build();
+        txn = new NodeUpdateBuilder()
+                .withNodeId(2L)
+                .withGossipCaCertificate(Bytes.wrap("not a cert"))
+                .build();
         given(handleContext.body()).willReturn(txn);
         final var config = HederaTestConfigBuilder.create()
                 .withValue("nodes.nodeMaxDescriptionUtf8Bytes", 10)
@@ -183,6 +218,33 @@ void nodeIdMustInState() {
         assertEquals(ResponseCodeEnum.INVALID_NODE_ID, msg.getStatus());
     }
 
+    @Test
+    void handleFailsWhenGossipCaCertificateExpiredAtConsensusTime() throws CertificateEncodingException {
+        final var cert = certList.getFirst();
+        txn = new NodeUpdateBuilder()
+                .withNodeId(1L)
+                .withGossipCaCertificate(Bytes.wrap(cert.getEncoded()))
+                .build();
+        setupMinimalHandle();
+        given(handleContext.consensusNow())
+                .willReturn(cert.getNotAfter().toInstant().plusSeconds(1));
+
+        final var msg = assertThrows(HandleException.class, () -> subject.handle(handleContext));
+        assertEquals(INVALID_GOSSIP_CA_CERTIFICATE, msg.getStatus());
+    }
+
+    @Test
+    void handleFailsWhenGossipCaCertificateIsInvalid() {
+        txn = new NodeUpdateBuilder()
+                .withNodeId(1L)
+                .withGossipCaCertificate(Bytes.wrap("not a cert"))
+                .build();
+        setupMinimalHandle();
+
+        final var msg = assertThrows(HandleException.class, () -> subject.handle(handleContext));
+        assertEquals(INVALID_GOSSIP_CA_CERTIFICATE, msg.getStatus());
+    }
+
     @Test
     void accountIdMustInState() {
         txn = new NodeUpdateBuilder().withNodeId(1L).withAccountId(accountId).build();
@@ -987,6 +1049,7 @@ private void setupWritableNodeStore(final Node node) {
 
     private void setupMinimalHandle() {
         given(handleContext.body()).willReturn(txn);
+        given(handleContext.consensusNow()).willReturn(VALID_CERT_TIME);
         final var config = HederaTestConfigBuilder.create()
                 .withValue("nodes.maxGossipEndpoint", 2)
                 .getOrCreateConfig();
```

### hedera-node/hedera-addressbook-service-impl/src/test/java/com/hedera/node/app/service/addressbook/impl/validators/AddressBookValidatorTest.java
```diff
@@ -12,6 +12,7 @@
 import static com.hedera.hapi.node.base.ResponseCodeEnum.REGISTERED_ENDPOINTS_EXCEEDED_LIMIT;
 import static com.hedera.node.app.service.addressbook.AddressBookHelper.writeCertificatePemFile;
 import static com.hedera.node.app.service.addressbook.impl.test.handlers.AddressBookTestBase.generateX509Certificates;
+import static com.hedera.node.app.service.addressbook.impl.validators.AddressBookValidator.parseX509Certificate;
 import static com.hedera.node.app.service.addressbook.impl.validators.AddressBookValidator.validateX509Certificate;
 import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
 import static org.junit.jupiter.api.Assertions.assertEquals;
@@ -57,15 +58,28 @@ static void beforeAll() {
 
     @Test
     void encodedCertPassesValidation() {
-        assertDoesNotThrow(() -> validateX509Certificate(Bytes.wrap(x509Cert.getEncoded())));
+        assertDoesNotThrow(() -> parseX509Certificate(Bytes.wrap(x509Cert.getEncoded())));
+    }
+
+    @Test
+    void encodedCertPassesValidationAtDeterministicTime() {
+        final var validAt = x509Cert.getNotBefore().toInstant().plusSeconds(1);
+        assertDoesNotThrow(() -> validateX509Certificate(Bytes.wrap(x509Cert.getEncoded()), validAt));
+    }
+
+    @Test
+    void encodedCertFailsValidationOutsideDeterministicTime() {
+        final var notYetValidAt = x509Cert.getNotBefore().toInstant().minusSeconds(1);
+        final var e = assertThrows(
+                HandleException.class, () -> validateX509Certificate(Bytes.wrap(x509Cert.getEncoded()), notYetValidAt));
+        assertEquals(INVALID_GOSSIP_CA_CERTIFICATE, e.getStatus());
     }
 
     @Test
     void utf8EncodingOfX509PemFailsValidation() throws CertificateEncodingException, IOException {
         final var baos = new ByteArrayOutputStream();
         writeCertificatePemFile(x509Cert.getEncoded(), baos);
-        final var e =
-                assertThrows(PreCheckException.class, () -> validateX509Certificate(Bytes.wrap(baos.toByteArray())));
+        final var e = assertThrows(PreCheckException.class, () -> parseX509Certificate(Bytes.wrap(baos.toByteArray())));
         assertEquals(INVALID_GOSSIP_CA_CERTIFICATE, e.responseCode());
     }
 
```
