# [?] Fixes: GHSA-p4h2-gvh4-pv6j reject non-empty withdrawals in BFT NotApplicableWithdrawals validator (#120)

## Summary
Severity: Unknown
Chain: Ethereum
Component: hyperledger/besu
Published: 2026-08-28
Source: https://github.com/besu-eth/besu/commit/ffe8104ee2c381cfe21901f70e77eca61ff9fcd3
Type: security-commit

## Details
Fixes: GHSA-p4h2-gvh4-pv6j reject non-empty withdrawals in BFT NotApplicableWithdrawals validator (#120)

* fix(consensus): reject non-empty withdrawals in BFT NotApplicableWithdrawals validator

Fixes: GHSA-p4h2-gvh4-pv6j
Fixes #119

NotApplicableWithdrawals previously returned true unconditionally, allowing
a Byzantine BFT proposer to inject arbitrary withdrawals that passed body
validation and were executed by WithdrawalsProcessor as native-balance
credits on all honest validators.

Fix both methods:
- validateWithdrawals: accept Optional.empty() (pre-Shanghai) or
  Optional.of(emptyList()) (Shanghai+); reject any non-empty list
- validateWithdrawalsRoot: accept absent root (pre-Shanghai); for
  Shanghai+ verify the root matches BodyValidation.withdrawalsRoot(List.of())

Adds four Byzantine-proposer regression tests covering: one injected
withdrawal, root mismatch with all-zero hash, non-empty list with
correct root, and duplicate withdrawal identity.

---------

Signed-off-by: Sally MacFarlane <sally.macfarlane@consensys.net>
Signed-off-by: Sally MacFarlane <macfarla.github@gmail.com>

## Patch
### consensus/qbft/src/test/java/org/hyperledger/besu/consensus/qbft/QbftProtocolScheduleBuilderTest.java
```diff
@@ -27,16 +27,23 @@
 import org.hyperledger.besu.consensus.common.ForksSchedule;
 import org.hyperledger.besu.consensus.common.bft.BftExtraDataCodec;
 import org.hyperledger.besu.consensus.common.bft.BftProtocolSchedule;
+import org.hyperledger.besu.datatypes.Address;
+import org.hyperledger.besu.datatypes.GWei;
 import org.hyperledger.besu.ethereum.chain.BadBlockManager;
 import org.hyperledger.besu.ethereum.core.MiningConfiguration;
+import org.hyperledger.besu.ethereum.core.Withdrawal;
 import org.hyperledger.besu.ethereum.mainnet.BalConfiguration;
 import org.hyperledger.besu.ethereum.mainnet.ProtocolSpec;
+import org.hyperledger.besu.ethereum.mainnet.WithdrawalsValidator;
 import org.hyperledger.besu.evm.internal.EvmConfiguration;
 import org.hyperledger.besu.metrics.noop.NoOpMetricsSystem;
 
 import java.util.List;
+import java.util.Optional;
 import java.util.OptionalLong;
 
+import com.fasterxml.jackson.databind.node.ObjectNode;
+import org.apache.tuweni.units.bigints.UInt64;
 import org.junit.jupiter.api.Test;
 
 public class QbftProtocolScheduleBuilderTest {
@@ -280,6 +287,45 @@ public void forkOmittingKeyRetainsPriorValue() {
         .isEqualTo(8_000_000L);
   }
 
+  @Test
+  public void shanghaiQbftSpecRejectsByzantineInjectedWithdrawals() {
+    // Regression test for GHSA-p4h2-gvh4-pv6j: verify that the BFT protocol schedule wires
+    // NotApplicableWithdrawals correctly for Shanghai, and that the validator rejects a
+    // Byzantine proposer's non-empty withdrawal list before it reaches WithdrawalsProcessor.
+    final long shanghaiTime = 0;
+    final ObjectNode genesisConfigNode = JsonUtil.createEmptyObjectNode();
+    genesisConfigNode.put("shanghaitime", shanghaiTime);
+
+    final BftProtocolSchedule schedule =
+        createProtocolSchedule(
+            JsonGenesisConfigOptions.fromJsonObject(genesisConfigNode),
+            List.of(new ForkSpec<>(0, JsonQbftConfigOptions.DEFAULT)));
+
+    final ProtocolSpec shanghaiSpec = schedule.getByBlockNumberOrTimestamp(1, shanghaiTime);
+    final WithdrawalsValidator validator = shanghaiSpec.getWithdrawalsValidator();
+
+    // Schedule must wire NotApplicableWithdrawals, not AllowedWithdrawals
+    assertThat(validator).isInstanceOf(WithdrawalsValidator.NotApplicableWithdrawals.class);
+
+    // Empty list (honest proposer) must be accepted
+    assertThat(validator.validateWithdrawals(Optional.of(List.of()))).isTrue();
+
+    // Byzantine proposer injects one withdrawal — must be rejected before execution
+    final List<Withdrawal> injected =
+        List.of(
+            new Withdrawal(
+                UInt64.valueOf(9001),
+                UInt64.valueOf(313),
+                Address.fromHexString("0x000000000000000000000000000000000000c0de"),
+                GWei.of(11)));
+    assertThat(validator.validateWithdrawals(Optional.of(injected))).isFalse();
+
+    // Multiple injected withdrawals also rejected
+    assertThat(
+            validator.validateWithdrawals(Optional.of(List.of(injected.get(0), injected.get(0)))))
+        .isFalse();
+  }
+
   private BftProtocolSchedule createProtocolSchedule(
       final JsonGenesisConfigOptions genesisConfig, final List<ForkSpec<QbftConfigOptions>> forks) {
     return QbftProtocolScheduleBuilder.create(
```

### ethereum/core/src/main/java/org/hyperledger/besu/ethereum/mainnet/WithdrawalsValidator.java
```diff
@@ -99,13 +99,36 @@ public boolean validateWithdrawalsRoot(final Block block) {
 
   class NotApplicableWithdrawals implements WithdrawalsValidator {
 
+    private static final Logger LOG = LoggerFactory.getLogger(NotApplicableWithdrawals.class);
+
     @Override
     public boolean validateWithdrawals(final Optional<List<Withdrawal>> withdrawals) {
+      // Pre-Shanghai blocks have no withdrawals field (Optional.empty()) — valid.
+      // Shanghai+ blocks must carry an empty list; a non-empty list means a Byzantine
+      // proposer injected unauthorized withdrawals that would be executed as balance credits.
+      if (withdrawals.isPresent() && !withdrawals.get().isEmpty()) {
+        LOG.warn(
+            "Withdrawals not applicable but block contained {} withdrawal(s)",
+            withdrawals.get().size());
+        return false;
+      }
       return true;
     }
 
     @Override
     public boolean validateWithdrawalsRoot(final Block block) {
+      final Optional<Hash> withdrawalsRoot = block.getHeader().getWithdrawalsRoot();
+      if (withdrawalsRoot.isEmpty()) {
+        return true; // pre-Shanghai block, no withdrawals root field
+      }
+      final Hash expectedRoot = Hash.EMPTY_TRIE_HASH;
+      if (!expectedRoot.equals(withdrawalsRoot.get())) {
+        LOG.warn(
+            "Invalid block: withdrawals root mismatch (expected={}, actual={})",
+            expectedRoot,
+            withdrawalsRoot.get());
+        return false;
+      }
       return true;
     }
   }
```

### ethereum/core/src/test/java/org/hyperledger/besu/ethereum/mainnet/WithdrawalsValidatorTest.java
```diff
@@ -17,13 +17,18 @@
 import static java.util.Collections.emptyList;
 import static org.assertj.core.api.Assertions.assertThat;
 
+import org.hyperledger.besu.datatypes.Address;
+import org.hyperledger.besu.datatypes.GWei;
 import org.hyperledger.besu.datatypes.Hash;
 import org.hyperledger.besu.ethereum.core.Block;
 import org.hyperledger.besu.ethereum.core.BlockDataGenerator;
+import org.hyperledger.besu.ethereum.core.Withdrawal;
 
 import java.util.Collections;
+import java.util.List;
 import java.util.Optional;
 
+import org.apache.tuweni.units.bigints.UInt64;
 import org.junit.jupiter.api.Test;
 
 public class WithdrawalsValidatorTest {
@@ -129,4 +134,68 @@ public void validateNotApplicableWithdrawalsRootWhenAbsent() {
     assertThat(new WithdrawalsValidator.NotApplicableWithdrawals().validateWithdrawalsRoot(block))
         .isTrue();
   }
+
+  // Byzantine-proposer regression tests for GHSA-p4h2-gvh4-pv6j:
+  // a proposer injecting non-empty withdrawals must be rejected before execution.
+
+  @Test
+  public void rejectsByzantineNonEmptyWithdrawalList() {
+    final List<Withdrawal> injected =
+        List.of(
+            new Withdrawal(
+                UInt64.valueOf(9001),
+                UInt64.valueOf(313),
+                Address.fromHexString("0x000000000000000000000000000000000000c0de"),
+                GWei.of(11)));
+    assertThat(
+            new WithdrawalsValidator.NotApplicableWithdrawals()
+                .validateWithdrawals(Optional.of(injected)))
+        .isFalse();
+  }
+
+  @Test
+  public void rejectsByzantineWithdrawalsRootMismatch() {
+    // Body has empty list but header declares a wrong root (all-zero, as in the PoC).
+    final BlockDataGenerator.BlockOptions blockOptions =
+        BlockDataGenerator.BlockOptions.create()
+            .setWithdrawals(Optional.of(Collections.emptyList()))
+            .setWithdrawalsRoot(Hash.ZERO);
+    final Block block = blockDataGenerator.block(blockOptions);
+    assertThat(new WithdrawalsValidator.NotApplicableWithdrawals().validateWithdrawalsRoot(block))
+        .isFalse();
+  }
+
+  @Test
+  public void rejectsByzantineNonEmptyWithdrawalsWithCorrectRoot() {
+    // Body has one real withdrawal and the header root correctly reflects it — still rejected
+    // because the list is non-empty.
+    final List<Withdrawal> injected =
+        List.of(
+            new Withdrawal(
+                UInt64.valueOf(9001),
+                UInt64.valueOf(313),
+                Address.fromHexString("0x000000000000000000000000000000000000c0de"),
+                GWei.of(11)));
+    final BlockDataGenerator.BlockOptions blockOptions =
+        BlockDataGenerator.BlockOptions.create().setWithdrawals(Optional.of(injected));
+    final Block block = blockDataGenerator.block(blockOptions);
+    assertThat(
+            new WithdrawalsValidator.NotApplicableWithdrawals()
+                .validateWithdrawals(block.getBody().getWithdrawals()))
+        .isFalse();
+  }
+
+  @Test
+  public void rejectsByzantineDuplicateWithdrawals() {
+    final Withdrawal w =
+        new Withdrawal(
+            UInt64.valueOf(7),
+            UInt64.valueOf(1),
+            Address.fromHexString("0x000000000000000000000000000000000000dead"),
+            GWei.of(7));
+    assertThat(
+            new WithdrawalsValidator.NotApplicableWithdrawals()
+                .validateWithdrawals(Optional.of(List.of(w, w))))
+        .isFalse();
+  }
 }
```
