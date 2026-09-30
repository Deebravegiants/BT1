# [?] fix: throw correct exception when token claim max amount is out of bounds, add hapi tests (#15113)

## Summary
Severity: Unknown
Chain: Hedera
Component: hiero-ledger/hiero-consensus-node
Published: 2024-08-28
Source: https://github.com/hiero-ledger/hiero-consensus-node/commit/05856af9ebb654f006941514ea4d0bdb91a46b12
Type: security-commit

## Details
fix: throw correct exception when token claim max amount is out of bounds, add hapi tests (#15113)

Signed-off-by: Lev Povolotsky <lev@swirldslabs.com>

## Patch
### hedera-node/hedera-token-service-impl/src/main/java/com/hedera/node/app/service/token/impl/WritableAirdropStore.java
```diff
@@ -72,36 +72,6 @@ public void put(@NonNull final PendingAirdropId airdropId, @NonNull final Accoun
         airdropState.put(airdropId, accountAirdrop);
     }
 
-    /**
-     * Persists a new {@link PendingAirdropId} with given {@link AccountPendingAirdrop} into the state.
-     * If there is existing airdrop with the same id we add the value to the existing drop.
-     *
-     * @param airdropId    - the airdropId to be persisted.
-     * @param accountAirdrop - the account airdrop mapping for the given airdropId to be persisted.
-     */
-    public void update(@NonNull final PendingAirdropId airdropId, @NonNull final AccountPendingAirdrop accountAirdrop) {
-        requireNonNull(airdropId);
-        requireNonNull(accountAirdrop);
-        if (!airdropState.contains(airdropId)) {
-            put(airdropId, accountAirdrop);
-            return;
-        }
-
-        if (airdropId.hasFungibleTokenType()) {
-            final var existingAirdrop = requireNonNull(airdropState.getForModify(airdropId));
-            final var existingValue = existingAirdrop.pendingAirdropValue();
-            final var newValue =
-                    requireNonNull(accountAirdrop.pendingAirdropValue()).amount()
-                            + requireNonNull(existingValue).amount();
-            final var newAccountAirdrop = existingAirdrop
-                    .copyBuilder()
-                    .pendingAirdropValue(
-                            existingValue.copyBuilder().amount(newValue).build())
-                    .build();
-            put(airdropId, newAccountAirdrop);
-        }
-    }
-
     /**
      * Removes a {@link PendingAirdropId} from the state
      *
```

### hedera-node/hedera-token-service-impl/src/main/java/com/hedera/node/app/service/token/impl/handlers/TokenAirdropHandler.java
```diff
@@ -17,6 +17,7 @@
 package com.hedera.node.app.service.token.impl.handlers;
 
 import static com.hedera.hapi.node.base.ResponseCodeEnum.INSUFFICIENT_PAYER_BALANCE;
+import static com.hedera.hapi.node.base.ResponseCodeEnum.INSUFFICIENT_TOKEN_BALANCE;
 import static com.hedera.hapi.node.base.ResponseCodeEnum.MAX_ENTITIES_IN_PRICE_REGIME_HAVE_BEEN_CREATED;
 import static com.hedera.hapi.node.base.ResponseCodeEnum.NOT_SUPPORTED;
 import static com.hedera.hapi.node.base.ResponseCodeEnum.PENDING_NFT_AIRDROP_ALREADY_EXISTS;
@@ -442,7 +443,7 @@ private void updateNewPendingAirdrop(
             @NonNull final WritableAirdropStore pendingStore) {
         if (pendingStore.contains(pendingId)) {
             // No need to update pointers to update the amount of fungible value
-            pendingStore.update(pendingId, createFirstAccountPendingAirdrop(pendingValue));
+            update(pendingId, createFirstAccountPendingAirdrop(pendingValue), pendingStore);
         } else {
             final AccountPendingAirdrop newHeadAirdrop;
             if (senderAccount.hasHeadPendingAirdropId()) {
@@ -570,4 +571,39 @@ private int countExistingPendingAirdrops(
                 .filter(pendingStore::exists)
                 .count());
     }
+
+    /**
+     * Persists a new {@link PendingAirdropId} with given {@link AccountPendingAirdrop} into the state.
+     * If there is existing airdrop with the same id we add the value to the existing drop.
+     *
+     * @param airdropId    - the airdropId to be persisted.
+     * @param accountAirdrop - the account airdrop mapping for the given airdropId to be persisted.
+     */
+    public void update(
+            @NonNull final PendingAirdropId airdropId,
+            @NonNull final AccountPendingAirdrop accountAirdrop,
+            @NonNull final WritableAirdropStore airdropState) {
+        requireNonNull(airdropId);
+        requireNonNull(accountAirdrop);
+        requireNonNull(airdropState);
+
+        if (airdropId.hasFungibleTokenType()) {
+            final var existingAirdrop = requireNonNull(airdropState.getForModify(airdropId));
+            final var existingValue = existingAirdrop.pendingAirdropValue();
+            long newValue;
+            try {
+                newValue = Math.addExact(
+                        requireNonNull(accountAirdrop.pendingAirdropValue()).amount(),
+                        requireNonNull(existingValue).amount());
+            } catch (ArithmeticException e) {
+                throw new HandleException(INSUFFICIENT_TOKEN_BALANCE);
+            }
+            final var newAccountAirdrop = existingAirdrop
+                    .copyBuilder()
+                    .pendingAirdropValue(
+                            existingValue.copyBuilder().amount(newValue).build())
+                    .build();
+            airdropState.put(airdropId, newAccountAirdrop);
+        }
+    }
 }
```

### hedera-node/hedera-token-service-impl/src/test/java/com/hedera/node/app/service/token/impl/test/WritableAirdropStoreTest.java
```diff
@@ -83,35 +83,6 @@ void putsAirdropsToState() {
         assertThat(airdropValue).isEqualTo(tokenValue);
     }
 
-    @Test
-    void updateUpdatesExistingAirdrop() {
-        final var airdropId = getFungibleAirdrop();
-        final var airdropValue = airdropWithValue(30);
-        final var accountAirdrop = accountAirdropWith(airdropValue);
-        writableAirdropState = emptyWritableAirdropStateBuilder()
-                .value(airdropId, accountAirdrop)
-                .build();
-        given(writableStates.<PendingAirdropId, AccountPendingAirdrop>get(AIRDROPS))
-                .willReturn(writableAirdropState);
-        subject = new WritableAirdropStore(writableStates, configuration, storeMetricsService);
-
-        final var newAirdropValue = airdropWithValue(20);
-        final var newAccountAirdrop = accountAirdrop
-                .copyBuilder()
-                .pendingAirdropValue(newAirdropValue)
-                .build();
-
-        assertThat(writableAirdropState.contains(airdropId)).isTrue();
-
-        subject.update(airdropId, newAccountAirdrop);
-
-        assertThat(writableAirdropState.contains(airdropId)).isTrue();
-        final var tokenValue = Objects.requireNonNull(Objects.requireNonNull(writableAirdropState.get(airdropId))
-                        .pendingAirdropValue())
-                .amount();
-        assertThat(tokenValue).isEqualTo(airdropValue.amount() + newAirdropValue.amount());
-    }
-
     @Test
     void putsDoesNotUpdateNftIfExists() {
         final var nftId = getNonFungibleAirDrop();
```

### hedera-node/hedera-token-service-impl/src/test/java/com/hedera/node/app/service/token/impl/test/handlers/TokenAirdropHandlerTest.java
```diff
@@ -44,17 +44,20 @@
 import com.hedera.hapi.node.base.SubType;
 import com.hedera.hapi.node.base.TokenID;
 import com.hedera.hapi.node.base.TokenTransferList;
+import com.hedera.hapi.node.state.token.AccountPendingAirdrop;
 import com.hedera.hapi.node.token.TokenAirdropTransactionBody;
 import com.hedera.hapi.node.transaction.PendingAirdropRecord;
 import com.hedera.hapi.node.transaction.TransactionBody;
 import com.hedera.node.app.fees.FeeContextImpl;
 import com.hedera.node.app.service.token.ReadableTokenStore;
+import com.hedera.node.app.service.token.impl.WritableAirdropStore;
 import com.hedera.node.app.service.token.impl.WritableTokenStore;
 import com.hedera.node.app.service.token.impl.handlers.TokenAirdropHandler;
 import com.hedera.node.app.service.token.records.TokenAirdropStreamBuilder;
 import com.hedera.node.app.spi.fees.FeeCalculator;
 import com.hedera.node.app.spi.fees.FeeCalculatorFactory;
 import com.hedera.node.app.spi.fees.Fees;
+import com.hedera.node.app.spi.metrics.StoreMetricsService;
 import com.hedera.node.app.spi.signatures.SignatureVerification;
 import com.hedera.node.app.spi.workflows.HandleException;
 import com.hedera.node.app.spi.workflows.PreCheckException;
@@ -90,6 +93,9 @@ class TokenAirdropHandlerTest extends CryptoTransferHandlerTestBase {
     @Mock
     private FeeCalculator feeCalculator;
 
+    @Mock
+    private StoreMetricsService storeMetricsService;
+
     @SuppressWarnings("DataFlowIssue")
     @Test
     void pureChecksNullArgThrows() {
@@ -522,6 +528,36 @@ void calculateFeesShouldChargeBaseFee() {
         assertEquals(30, fees.serviceFee());
     }
 
+    @Test
+    void updateUpdatesExistingAirdrop() {
+        final var airdropId = getFungibleAirdrop();
+        final var airdropValue = airdropWithValue(30);
+        final var accountAirdrop = accountAirdropWith(airdropValue);
+        writableAirdropState = emptyWritableAirdropStateBuilder()
+                .value(airdropId, accountAirdrop)
+                .build();
+        given(writableStates.<PendingAirdropId, AccountPendingAirdrop>get(AIRDROPS))
+                .willReturn(writableAirdropState);
+        writableAirdropStore = new WritableAirdropStore(writableStates, configuration, storeMetricsService);
+        tokenAirdropHandler = new TokenAirdropHandler(tokenAirdropValidator, validator);
+
+        final var newAirdropValue = airdropWithValue(20);
+        final var newAccountAirdrop = accountAirdrop
+                .copyBuilder()
+                .pendingAirdropValue(newAirdropValue)
+                .build();
+
+        Assertions.assertThat(writableAirdropState.contains(airdropId)).isTrue();
+
+        tokenAirdropHandler.update(airdropId, newAccountAirdrop, writableAirdropStore);
+
+        Assertions.assertThat(writableAirdropState.contains(airdropId)).isTrue();
+        final var tokenValue = Objects.requireNonNull(Objects.requireNonNull(writableAirdropState.get(airdropId))
+                        .pendingAirdropValue())
+                .amount();
+        Assertions.assertThat(tokenValue).isEqualTo(airdropValue.amount() + newAirdropValue.amount());
+    }
+
     private void setupAirdropMocks(TokenAirdropTransactionBody body, boolean enableAirdrop) {
         when(feeContext.body()).thenReturn(transactionBody);
         when(transactionBody.tokenAirdropOrThrow()).thenReturn(body);
@@ -544,4 +580,21 @@ private List<TokenTransferList> transactionBodyAboveMaxTransferLimit() {
 
         return result;
     }
+
+    private PendingAirdropId getFungibleAirdrop() {
+        return PendingAirdropId.newBuilder()
+                .fungibleTokenType(
+                        TokenID.newBuilder().realmNum(1).shardNum(2).tokenNum(3).build())
+                .build();
+    }
+
+    private PendingAirdropValue airdropWithValue(long value) {
+        return PendingAirdropValue.newBuilder().amount(value).build();
+    }
+
+    private AccountPendingAirdrop accountAirdropWith(PendingAirdropValue pendingAirdropValue) {
+        return AccountPendingAirdrop.newBuilder()
+                .pendingAirdropValue(pendingAirdropValue)
+                .build();
+    }
 }
```

### hedera-node/test-clients/src/main/java/com/hedera/services/bdd/spec/utilops/EmbeddedVerbs.java
```diff
@@ -18,11 +18,13 @@
 
 import com.hedera.hapi.node.state.addressbook.Node;
 import com.hedera.hapi.node.state.token.Account;
+import com.hedera.hapi.node.state.token.AccountPendingAirdrop;
 import com.hedera.services.bdd.junit.hedera.embedded.EmbeddedNetwork;
 import com.hedera.services.bdd.spec.utilops.embedded.MutateAccountOp;
 import com.hedera.services.bdd.spec.utilops.embedded.MutateNodeOp;
 import com.hedera.services.bdd.spec.utilops.embedded.ViewAccountOp;
 import com.hedera.services.bdd.spec.utilops.embedded.ViewNodeOp;
+import com.hedera.services.bdd.spec.utilops.embedded.ViewPendingAirdropOp;
 import edu.umd.cs.findbugs.annotations.NonNull;
 import java.util.function.Consumer;
 
@@ -78,4 +80,20 @@ public static MutateNodeOp mutateNode(@NonNull final String name, @NonNull final
     public static ViewNodeOp viewNode(@NonNull final String name, @NonNull final Consumer<Node> observer) {
         return new ViewNodeOp(name, observer);
     }
+
+    /***
+     * `ViewPendingAirdropOp` is an operation that allows the test author to view the pending airdrop of an account.
+     * @param tokenName
+     * @param senderName
+     * @param receiverName
+     * @param observer
+     * @return
+     */
+    public static ViewPendingAirdropOp viewAccountPendingAirdrop(
+            @NonNull final String tokenName,
+            @NonNull final String senderName,
+            @NonNull final String receiverName,
+            @NonNull final Consumer<AccountPendingAirdrop> observer) {
+        return new ViewPendingAirdropOp(tokenName, senderName, receiverName, observer);
+    }
 }
```

### hedera-node/test-clients/src/main/java/com/hedera/services/bdd/spec/utilops/embedded/ViewPendingAirdropOp.java
```diff
@@ -0,0 +1,65 @@
+/*
+ * Copyright (C) 2024 Hedera Hashgraph, LLC
+ *
+ * Licensed under the Apache License, Version 2.0 (the "License");
+ * you may not use this file except in compliance with the License.
+ * You may obtain a copy of the License at
+ *
+ *      http://www.apache.org/licenses/LICENSE-2.0
+ *
+ * Unless required by applicable law or agreed to in writing, software
+ * distributed under the License is distributed on an "AS IS" BASIS,
+ * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
+ * See the License for the specific language governing permissions and
+ * limitations under the License.
+ */
+
+package com.hedera.services.bdd.spec.utilops.embedded;
+
+import static com.hedera.node.app.hapi.utils.CommonPbjConverters.toPbj;
+import static com.hedera.node.app.service.token.TokenService.NAME;
+import static com.hedera.node.app.service.token.impl.schemas.V0530TokenSchema.AIRDROPS_KEY;
+import static java.util.Objects.requireNonNull;
+
+import com.hedera.hapi.node.base.PendingAirdropId;
+import com.hedera.hapi.node.state.token.AccountPendingAirdrop;
+import com.hedera.services.bdd.spec.HapiSpec;
+import com.hedera.services.bdd.spec.transactions.TxnUtils;
+import com.hedera.services.bdd.spec.utilops.UtilOp;
+import com.swirlds.state.spi.ReadableKVState;
+import edu.umd.cs.findbugs.annotations.NonNull;
+import java.util.function.Consumer;
+
+public class ViewPendingAirdropOp extends UtilOp {
+    private final String tokenName;
+    private final String senderName;
+    private final String receiverName;
+    private final Consumer<AccountPendingAirdrop> observer;
+
+    public ViewPendingAirdropOp(
+            @NonNull final String tokenName,
+            @NonNull final String senderName,
+            @NonNull final String receiverName,
+            @NonNull final Consumer<AccountPendingAirdrop> observer) {
+        this.tokenName = requireNonNull(tokenName);
+        this.receiverName = requireNonNull(receiverName);
+        this.senderName = requireNonNull(senderName);
+        this.observer = requireNonNull(observer);
+    }
+
+    @Override
+    protected boolean submitOp(@NonNull final HapiSpec spec) throws Throwable {
+        final var state = spec.embeddedStateOrThrow();
+        final var readableStates = state.getReadableStates(NAME);
+        final ReadableKVState<PendingAirdropId, AccountPendingAirdrop> readableAirdropState =
+                readableStates.get(AIRDROPS_KEY);
+        final var pendingAirdropId = PendingAirdropId.newBuilder()
+                .receiverId(toPbj(TxnUtils.asId(receiverName, spec)))
+                .senderId(toPbj(TxnUtils.asId(senderName, spec)))
+                .fungibleTokenType(toPbj(TxnUtils.asTokenId(tokenName, spec)))
+                .build();
+        final var accountPendingAirdrop = readableAirdropState.get(pendingAirdropId);
+        observer.accept(accountPendingAirdrop);
+        return false;
+    }
+}
```

### hedera-node/test-clients/src/main/java/com/hedera/services/bdd/suites/hip904/TokenAirdropTest.java
```diff
@@ -92,17 +92,21 @@
 
 import com.google.protobuf.ByteString;
 import com.hedera.node.app.hapi.utils.ByteStringUtils;
+import com.hedera.services.bdd.junit.EmbeddedHapiTest;
+import com.hedera.services.bdd.junit.EmbeddedReason;
 import com.hedera.services.bdd.junit.HapiTest;
 import com.hedera.services.bdd.junit.HapiTestLifecycle;
 import com.hedera.services.bdd.junit.support.TestLifecycle;
 import com.hedera.services.bdd.spec.keys.SigControl;
 import com.hedera.services.bdd.spec.transactions.token.TokenMovement;
+import com.hedera.services.bdd.spec.utilops.EmbeddedVerbs;
 import com.hederahashgraph.api.proto.java.TokenID;
 import com.swirlds.common.utility.CommonUtils;
 import edu.umd.cs.findbugs.annotations.NonNull;
 import java.util.List;
 import java.util.Map;
 import java.util.stream.Stream;
+import org.junit.jupiter.api.Assertions;
 import org.junit.jupiter.api.BeforeAll;
 import org.junit.jupiter.api.DisplayName;
 import org.junit.jupiter.api.DynamicTest;
@@ -1810,6 +1814,49 @@ final Stream<DynamicTest> airdropTo0x0Address() {
         }
     }
 
+    @EmbeddedHapiTest(EmbeddedReason.NEEDS_STATE_ACCESS)
+    @DisplayName("verify that two fungible tokens airdrops combined into one pending airdrop")
+    final Stream<DynamicTest> twoFungibleTokenCombinedIntoOneAirdrop() {
+        final String ALICE = "alice";
+        final String BOB = "bob";
+        final String FUNGIBLE_TOKEN_A = "fungibleTokenA";
+        return hapiTest(
+                cryptoCreate(ALICE).balance(ONE_HUNDRED_HBARS),
+                cryptoCreate(BOB).balance(ONE_HUNDRED_HBARS),
+                tokenCreate(FUNGIBLE_TOKEN_A)
+                        .treasury(ALICE)
+                        .tokenType(FUNGIBLE_COMMON)
+                        .initialSupply(100L),
+                tokenAirdrop(moving(1, FUNGIBLE_TOKEN_A).between(ALICE, BOB)).signedByPayerAnd(ALICE),
+                tokenAirdrop(moving(1, FUNGIBLE_TOKEN_A).between(ALICE, BOB)).signedByPayerAnd(ALICE),
+                EmbeddedVerbs.viewAccountPendingAirdrop(
+                        FUNGIBLE_TOKEN_A,
+                        ALICE,
+                        BOB,
+                        pendingAirdrop -> Assertions.assertEquals(
+                                2, pendingAirdrop.pendingAirdropValueOrThrow().amount())));
+    }
+
+    @HapiTest
+    @DisplayName("max supply hit - max long value")
+    final Stream<DynamicTest> fungibleTokenMaxSupplyHit() {
+        final String ALICE = "alice";
+        final String BOB = "bob";
+        final String FUNGIBLE_TOKEN_A = "fungibleTokenA";
+        return hapiTest(
+                cryptoCreate(ALICE).balance(ONE_HUNDRED_HBARS),
+                cryptoCreate(BOB).balance(ONE_HUNDRED_HBARS),
+                tokenCreate(FUNGIBLE_TOKEN_A)
+                        .treasury(ALICE)
+                        .tokenType(FUNGIBLE_COMMON)
+                        .initialSupply(Long.MAX_VALUE),
+                tokenAirdrop(moving(Long.MAX_VALUE, FUNGIBLE_TOKEN_A).between(ALICE, BOB))
+                        .signedByPayerAnd(ALICE),
+                tokenAirdrop(moving(Long.MAX_VALUE, FUNGIBLE_TOKEN_A).between(ALICE, BOB))
+                        .signedByPayerAnd(ALICE)
+                        .hasKnownStatus(INSUFFICIENT_TOKEN_BALANCE));
+    }
+
     @Nested
     @DisplayName("delete account with relation ")
     class DeleteAccount {
```

### hedera-node/test-clients/src/main/java/com/hedera/services/bdd/suites/hip904/TokenClaimAirdropTest.java
```diff
@@ -44,6 +44,7 @@
 import static com.hedera.services.bdd.spec.transactions.TxnVerbs.tokenFreeze;
 import static com.hedera.services.bdd.spec.transactions.TxnVerbs.tokenPause;
 import static com.hedera.services.bdd.spec.transactions.TxnVerbs.tokenUpdate;
+import static com.hedera.services.bdd.spec.transactions.crypto.HapiCryptoTransfer.tinyBarsFromAccountToAlias;
 import static com.hedera.services.bdd.spec.transactions.crypto.HapiCryptoTransfer.tinyBarsFromTo;
 import static com.hedera.services.bdd.spec.transactions.token.HapiTokenClaimAirdrop.pendingAirdrop;
 import static com.hedera.services.bdd.spec.transactions.token.HapiTokenClaimAirdrop.pendingNFTAirdrop;
@@ -52,6 +53,7 @@
 import static com.hedera.services.bdd.spec.utilops.CustomSpecAssert.allRunFor;
 import static com.hedera.services.bdd.spec.utilops.UtilVerbs.blockingOrder;
 import static com.hedera.services.bdd.spec.utilops.UtilVerbs.inParallel;
+import static com.hedera.services.bdd.spec.utilops.UtilVerbs.logIt;
 import static com.hedera.services.bdd.spec.utilops.UtilVerbs.newKeyNamed;
 import static com.hedera.services.bdd.spec.utilops.UtilVerbs.overriding;
 import static com.hedera.services.bdd.spec.utilops.UtilVerbs.validateChargedUsd;
@@ -1100,6 +1102,39 @@ final Stream<DynamicTest> duplicateAirdropsFail() {
                         .hasPrecheck(PENDING_AIRDROP_ID_REPEATED)));
     }
 
+    @LeakyHapiTest(overrides = {"entities.unlimitedAutoAssociationsEnabled"})
+    @DisplayName("account created with same alias should fail")
+    final Stream<DynamicTest> accountCreatedWithSAmeAliasShouldFail() {
+        final String ALIAS = "alias";
+        return hapiTest(
+                // add common entities, you can create your own ones
+                flattened(
+                        setUpTokensAndAllReceivers(),
+                        logIt("preparation is over"),
+                        // stop the unlimitedAutoAssociations, in order to create the account and send the airdrop to
+                        overriding("entities.unlimitedAutoAssociationsEnabled", "false"),
+                        // create key
+                        newKeyNamed(ALIAS),
+                        // create first aliased account
+                        cryptoTransfer(tinyBarsFromAccountToAlias(OWNER, ALIAS, 1)),
+                        // save aliased account into registry
+                        withOpContext((spec, opLog) -> updateSpecFor(spec, ALIAS)),
+                        // airdrop
+                        tokenAirdrop(moving(1, FUNGIBLE_TOKEN).between(OWNER, ALIAS))
+                                .payingWith(OWNER),
+                        // airdrop should be pending, you can assert txn record too
+                        getAccountBalance(ALIAS).hasTokenBalance(FUNGIBLE_TOKEN, 0),
+                        // delete the account
+                        cryptoDelete(ALIAS),
+                        // create new account with the same key
+                        cryptoTransfer(tinyBarsFromAccountToAlias(OWNER, ALIAS, 1)),
+                        withOpContext((spec, opLog) -> updateSpecFor(spec, ALIAS)),
+                        // try to claim
+                        tokenClaimAirdrop(pendingAirdrop(OWNER, ALIAS, FUNGIBLE_TOKEN))
+                                .signedBy(ALIAS, DEFAULT_PAYER)
+                                .hasKnownStatus(INVALID_PENDING_AIRDROP_ID)));
+    }
+
     @HapiTest
     @DisplayName(
             "not signed by the account referenced by a receiver_id for each entry in the pending airdrops list should fail")
```
