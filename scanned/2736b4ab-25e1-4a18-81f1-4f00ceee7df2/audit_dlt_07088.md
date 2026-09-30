# [?] Fix ETH65 causes crashes issues (#1601)

## Summary
Severity: Unknown
Chain: Ethereum
Component: hyperledger/besu
Published: 2020-12-01
Source: https://github.com/besu-eth/besu/commit/d4a330b81e5ad63a4b220a4f2c4f0e82682af104
Type: security-commit

## Details
Fix ETH65 causes crashes issues (#1601)

This PR adds a waiting list for NewPooledTransactionHashesMessage in order to group several hashes into a single GetPooledTransactionsFromPeerTask

Signed-off-by: Karim TAAM <karim.t2am@gmail.com>

Co-authored-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

## Patch
### CHANGELOG.md
```diff
@@ -12,10 +12,10 @@
 * Ibft2 will discard any received messages targeting a chain height <= current head - this resolves some corner cases in system correctness directly following block import. [#1575](https://github.com/hyperledger/besu/pull/1575)
 * EvmTool now throws `UnsupportedForkException` when there is an unknown fork and is YOLOv2 compatible [\#1584](https://github.com/hyperledger/besu/pull/1584)
 * `eth_newFilter` now supports `blockHash` parameter as per the spec [\#1548](https://github.com/hyperledger/besu/issues/1540). (`blockhash` is also still supported.)
+* Fixed an issue that caused loss of peers and desynchronization when eth65 was enabled [\#1601](https://github.com/hyperledger/besu/pull/1601)
 
 #### Previously identified known issues
 
-- [Eth/65 loses peers](KNOWN_ISSUES.md#eth65-loses-peers)
 - [Fast sync when running Besu on cloud providers](KNOWN_ISSUES.md#fast-sync-when-running-besu-on-cloud-providers)
 - [Privacy users with private transactions created using v1.3.4 or earlier](KNOWN_ISSUES.md#privacy-users-with-private-transactions-created-using-v134-or-earlier)
 
```

### KNOWN_ISSUES.md
```diff
@@ -5,14 +5,6 @@ in the current release are provided in the [Changelog](CHANGELOG.md).
 
 Known issues are open issues categorized as [Very High or High impact](https://wiki.hyperledger.org/display/BESU/Defect+Prioritisation+Policy). 
 
-## Eth/65 loses peers 
-
-From v1.4.4, `eth/65` is [disabled by default](https://github.com/hyperledger/besu/pull/741). 
-
-If enabled, peers will slowly drop off and eventually Besu will fall out of sync or stop syncing.
-
-A fix for this issue is being actively worked on. 
-
 ## Fast sync when running Besu on cloud providers  
 
 A known [RocksDB issue](https://github.com/facebook/rocksdb/issues/6435) causes fast sync to fail 
```

### acceptance-tests/dsl/src/main/java/org/hyperledger/besu/tests/acceptance/dsl/node/ThreadBesuNodeRunner.java
```diff
@@ -156,7 +156,7 @@ public void startNode(final BesuNode node) {
             .privacyParameters(node.getPrivacyParameters())
             .nodeKey(new NodeKey(new KeyPairSecurityModule(KeyPairUtil.loadKeyPair(dataDir))))
             .metricsSystem(metricsSystem)
-            .transactionPoolConfiguration(TransactionPoolConfiguration.builder().build())
+            .transactionPoolConfiguration(TransactionPoolConfiguration.DEFAULT)
             .ethProtocolConfiguration(EthProtocolConfiguration.defaultConfig())
             .clock(Clock.systemUTC())
             .isRevertReasonEnabled(node.isRevertReasonEnabled())
```

### besu/src/main/java/org/hyperledger/besu/cli/BesuCommand.java
```diff
@@ -146,6 +146,7 @@
 import org.hyperledger.besu.util.NetworkUtility;
 import org.hyperledger.besu.util.PermissioningConfigurationValidator;
 import org.hyperledger.besu.util.number.Fraction;
+import org.hyperledger.besu.util.number.Percentage;
 import org.hyperledger.besu.util.number.PositiveNumber;
 
 import java.io.File;
@@ -2077,7 +2078,7 @@ private TransactionPoolConfiguration buildTransactionPoolConfiguration() {
         .txPoolMaxSize(txPoolMaxSize)
         .pooledTransactionHashesSize(pooledTransactionHashesSize)
         .pendingTxRetentionPeriod(pendingTxRetentionPeriod)
-        .priceBump(priceBump)
+        .priceBump(Percentage.fromInt(priceBump))
         .txFeeCap(txFeeCap)
         .build();
   }
```

### besu/src/main/java/org/hyperledger/besu/cli/options/unstable/TransactionPoolOptions.java
```diff
@@ -16,17 +16,23 @@
 
 import org.hyperledger.besu.cli.options.CLIOptions;
 import org.hyperledger.besu.cli.options.OptionParser;
+import org.hyperledger.besu.ethereum.eth.transactions.ImmutableTransactionPoolConfiguration;
 import org.hyperledger.besu.ethereum.eth.transactions.TransactionPoolConfiguration;
 
+import java.time.Duration;
 import java.util.Arrays;
 import java.util.List;
 
 import picocli.CommandLine;
 
-public class TransactionPoolOptions implements CLIOptions<TransactionPoolConfiguration.Builder> {
+public class TransactionPoolOptions
+    implements CLIOptions<ImmutableTransactionPoolConfiguration.Builder> {
   private static final String TX_MESSAGE_KEEP_ALIVE_SEC_FLAG =
       "--Xincoming-tx-messages-keep-alive-seconds";
 
+  private static final String ETH65_TX_ANNOUNCED_BUFFERING_PERIOD_FLAG =
+      "--Xeth65-tx-announced-buffering-period-milliseconds";
+
   @CommandLine.Option(
       names = {TX_MESSAGE_KEEP_ALIVE_SEC_FLAG},
       paramLabel = "<INTEGER>",
@@ -37,6 +43,16 @@ public class TransactionPoolOptions implements CLIOptions<TransactionPoolConfigu
   private Integer txMessageKeepAliveSeconds =
       TransactionPoolConfiguration.DEFAULT_TX_MSG_KEEP_ALIVE;
 
+  @CommandLine.Option(
+      names = {ETH65_TX_ANNOUNCED_BUFFERING_PERIOD_FLAG},
+      paramLabel = "<LONG>",
+      hidden = true,
+      description =
+          "The period for which the announced transactions remain in the buffer before being requested from the peers in milliseconds (default: ${DEFAULT-VALUE})",
+      arity = "1")
+  private long eth65TrxAnnouncedBufferingPeriod =
+      TransactionPoolConfiguration.ETH65_TRX_ANNOUNCED_BUFFERING_PERIOD.toMillis();
+
   private TransactionPoolOptions() {}
 
   public static TransactionPoolOptions create() {
@@ -46,18 +62,24 @@ public static TransactionPoolOptions create() {
   public static TransactionPoolOptions fromConfig(final TransactionPoolConfiguration config) {
     final TransactionPoolOptions options = TransactionPoolOptions.create();
     options.txMessageKeepAliveSeconds = config.getTxMessageKeepAliveSeconds();
+    options.eth65TrxAnnouncedBufferingPeriod =
+        config.getEth65TrxAnnouncedBufferingPeriod().toMillis();
     return options;
   }
 
   @Override
-  public TransactionPoolConfiguration.Builder toDomainObject() {
-    return TransactionPoolConfiguration.builder()
-        .txMessageKeepAliveSeconds(txMessageKeepAliveSeconds);
+  public ImmutableTransactionPoolConfiguration.Builder toDomainObject() {
+    return ImmutableTransactionPoolConfiguration.builder()
+        .txMessageKeepAliveSeconds(txMessageKeepAliveSeconds)
+        .eth65TrxAnnouncedBufferingPeriod(Duration.ofMillis(eth65TrxAnnouncedBufferingPeriod));
   }
 
   @Override
   public List<String> getCLIOptions() {
     return Arrays.asList(
-        TX_MESSAGE_KEEP_ALIVE_SEC_FLAG, OptionParser.format(txMessageKeepAliveSeconds));
+        TX_MESSAGE_KEEP_ALIVE_SEC_FLAG,
+        OptionParser.format(txMessageKeepAliveSeconds),
+        ETH65_TX_ANNOUNCED_BUFFERING_PERIOD_FLAG,
+        OptionParser.format(eth65TrxAnnouncedBufferingPeriod));
   }
 }
```

### besu/src/test/java/org/hyperledger/besu/PrivacyReorgTest.java
```diff
@@ -167,7 +167,7 @@ public void setUp() throws IOException {
             .dataDirectory(dataDir)
             .clock(TestClock.fixed())
             .privacyParameters(privacyParameters)
-            .transactionPoolConfiguration(TransactionPoolConfiguration.builder().build())
+            .transactionPoolConfiguration(TransactionPoolConfiguration.DEFAULT)
             .gasLimitCalculator(GasLimitCalculator.constant())
             .build();
   }
```

### besu/src/test/java/org/hyperledger/besu/PrivacyTest.java
```diff
@@ -113,7 +113,7 @@ private BesuController setUpControllerWithPrivacyEnabled(final boolean onChainEn
         .dataDirectory(dataDir)
         .clock(TestClock.fixed())
         .privacyParameters(privacyParameters)
-        .transactionPoolConfiguration(TransactionPoolConfiguration.builder().build())
+        .transactionPoolConfiguration(TransactionPoolConfiguration.DEFAULT)
         .gasLimitCalculator(GasLimitCalculator.constant())
         .build();
   }
```

### besu/src/test/java/org/hyperledger/besu/RunnerTest.java
```diff
@@ -164,7 +164,7 @@ private void syncFromGenesis(final SyncMode mode, final GenesisConfigFile genesi
             .metricsSystem(noOpMetricsSystem)
             .privacyParameters(PrivacyParameters.DEFAULT)
             .clock(TestClock.fixed())
-            .transactionPoolConfiguration(TransactionPoolConfiguration.builder().build())
+            .transactionPoolConfiguration(TransactionPoolConfiguration.DEFAULT)
             .storageProvider(createKeyValueStorageProvider(dataDirAhead, dbAhead))
             .gasLimitCalculator(GasLimitCalculator.constant())
             .build()) {
@@ -184,7 +184,7 @@ private void syncFromGenesis(final SyncMode mode, final GenesisConfigFile genesi
             .metricsSystem(noOpMetricsSystem)
             .privacyParameters(PrivacyParameters.DEFAULT)
             .clock(TestClock.fixed())
-            .transactionPoolConfiguration(TransactionPoolConfiguration.builder().build())
+            .transactionPoolConfiguration(TransactionPoolConfiguration.DEFAULT)
             .storageProvider(createKeyValueStorageProvider(dataDirAhead, dbAhead))
             .gasLimitCalculator(GasLimitCalculator.constant())
             .build();
@@ -248,7 +248,7 @@ private void syncFromGenesis(final SyncMode mode, final GenesisConfigFile genesi
               .metricsSystem(noOpMetricsSystem)
               .privacyParameters(PrivacyParameters.DEFAULT)
               .clock(TestClock.fixed())
-              .transactionPoolConfiguration(TransactionPoolConfiguration.builder().build())
+              .transactionPoolConfiguration(TransactionPoolConfiguration.DEFAULT)
               .gasLimitCalculator(GasLimitCalculator.constant())
               .build();
       final EnodeURL enode = runnerAhead.getLocalEnode().get();
```

### besu/src/test/java/org/hyperledger/besu/chainexport/RlpBlockExporterTest.java
```diff
@@ -90,7 +90,7 @@ private static BesuController createController() throws IOException {
         .privacyParameters(PrivacyParameters.DEFAULT)
         .dataDirectory(dataDir)
         .clock(TestClock.fixed())
-        .transactionPoolConfiguration(TransactionPoolConfiguration.builder().build())
+        .transactionPoolConfiguration(TransactionPoolConfiguration.DEFAULT)
         .gasLimitCalculator(GasLimitCalculator.constant())
         .build();
   }
```

### besu/src/test/java/org/hyperledger/besu/chainimport/JsonBlockImporterTest.java
```diff
@@ -427,7 +427,7 @@ protected BesuController createController(final GenesisConfigFile genesisConfigF
         .privacyParameters(PrivacyParameters.DEFAULT)
         .dataDirectory(dataDir)
         .clock(TestClock.fixed())
-        .transactionPoolConfiguration(TransactionPoolConfiguration.builder().build())
+        .transactionPoolConfiguration(TransactionPoolConfiguration.DEFAULT)
         .gasLimitCalculator(GasLimitCalculator.constant())
         .build();
   }
```

### besu/src/test/java/org/hyperledger/besu/chainimport/RlpBlockImporterTest.java
```diff
@@ -70,7 +70,7 @@ public void blockImport() throws IOException {
             .privacyParameters(PrivacyParameters.DEFAULT)
             .dataDirectory(dataDir)
             .clock(TestClock.fixed())
-            .transactionPoolConfiguration(TransactionPoolConfiguration.builder().build())
+            .transactionPoolConfiguration(TransactionPoolConfiguration.DEFAULT)
             .gasLimitCalculator(GasLimitCalculator.constant())
             .build();
     final RlpBlockImporter.ImportResult result =
@@ -98,7 +98,7 @@ public void blockImportRejectsBadPow() throws IOException {
             .privacyParameters(PrivacyParameters.DEFAULT)
             .dataDirectory(dataDir)
             .clock(TestClock.fixed())
-            .transactionPoolConfiguration(TransactionPoolConfiguration.builder().build())
+            .transactionPoolConfiguration(TransactionPoolConfiguration.DEFAULT)
             .gasLimitCalculator(GasLimitCalculator.constant())
             .build();
 
@@ -126,7 +126,7 @@ public void blockImportCanSkipPow() throws IOException {
             .privacyParameters(PrivacyParameters.DEFAULT)
             .dataDirectory(dataDir)
             .clock(TestClock.fixed())
-            .transactionPoolConfiguration(TransactionPoolConfiguration.builder().build())
+            .transactionPoolConfiguration(TransactionPoolConfiguration.DEFAULT)
             .gasLimitCalculator(GasLimitCalculator.constant())
             .build();
 
@@ -166,7 +166,7 @@ public void ibftImport() throws IOException {
             .privacyParameters(PrivacyParameters.DEFAULT)
             .dataDirectory(dataDir)
             .clock(TestClock.fixed())
-            .transactionPoolConfiguration(TransactionPoolConfiguration.builder().build())
+            .transactionPoolConfiguration(TransactionPoolConfiguration.DEFAULT)
             .gasLimitCalculator(GasLimitCalculator.constant())
             .build();
     final RlpBlockImporter.ImportResult result =
```

### besu/src/test/java/org/hyperledger/besu/cli/BesuCommandTest.java
```diff
@@ -3411,6 +3411,18 @@ public void txMessageKeepAliveSecondsWithInvalidInputShouldFail() {
             "Invalid value for option '--Xincoming-tx-messages-keep-alive-seconds': 'acbd' is not an int");
   }
 
+  @Test
+  public void eth65TrxAnnouncedBufferingPeriodWithInvalidInputShouldFail() {
+    parseCommand("--Xeth65-tx-announced-buffering-period-milliseconds", "acbd");
+
+    Mockito.verifyZeroInteractions(mockRunnerBuilder);
+
+    assertThat(commandOutput.toString()).isEmpty();
+    assertThat(commandErrorOutput.toString())
+        .contains(
+            "Invalid value for option '--Xeth65-tx-announced-buffering-period-milliseconds': 'acbd' is not a long");
+  }
+
   @Test
   public void tomlThatHasInvalidOptions() throws IOException {
     final URL configFile = this.getClass().getResource("/complete_config.toml");
```
