# [?] Merge pull request #7239 from rob-stacks/fix/pox5-contract-reentrancy

## Summary
Severity: Unknown
Chain: Stacks
Component: stacks-network/stacks-core
Published: 2026-06-05
Source: https://github.com/stacks-network/stacks-core/commit/a5aa93a4511a45463c8689485b9867b7f552ab1d
Type: security-commit

## Details
Merge pull request #7239 from rob-stacks/fix/pox5-contract-reentrancy

Fix/pox5 contract reentrancy

## Patch
### contrib/core-contract-tests/tests/clarigen-types.ts
```diff
@@ -4167,6 +4167,36 @@ export const contracts = {
           rewardsPerToken: bigint;
         }
       >,
+      signerManagerValidateStake: {
+        name: 'signer-manager-validate-stake',
+        access: 'private',
+        args: [
+          { name: 'signer-manager', type: 'trait_reference' },
+          { name: 'staker', type: 'principal' },
+          { name: 'first-index', type: 'uint128' },
+          { name: 'num-indexes', type: 'uint128' },
+          { name: 'amount-ustx', type: 'uint128' },
+          { name: 'amount-sats', type: 'uint128' },
+          { name: 'is-bond', type: 'bool' },
+          {
+            name: 'signer-calldata',
+            type: { optional: { buffer: { length: 500 } } },
+          },
+        ],
+        outputs: { type: { response: { ok: 'bool', error: 'uint128' } } },
+      } as TypedAbiFunction<
+        [
+          signerManager: TypedAbiArg<string, 'signerManager'>,
+          staker: TypedAbiArg<string, 'staker'>,
+          firstIndex: TypedAbiArg<number | bigint, 'firstIndex'>,
+          numIndexes: TypedAbiArg<number | bigint, 'numIndexes'>,
+          amountUstx: TypedAbiArg<number | bigint, 'amountUstx'>,
+          amountSats: TypedAbiArg<number | bigint, 'amountSats'>,
+          isBond: TypedAbiArg<boolean, 'isBond'>,
+          signerCalldata: TypedAbiArg<Uint8Array | null, 'signerCalldata'>,
+        ],
+        Response<boolean, bigint>
+      >,
       updateClaimableBondRewards: {
         name: 'update-claimable-bond-rewards',
         access: 'private',
@@ -4404,6 +4434,12 @@ export const contracts = {
           bigint
         >
       >,
+      validateNoReentrancy: {
+        name: 'validate-no-reentrancy',
+        access: 'private',
+        args: [],
+        outputs: { type: { response: { ok: 'bool', error: 'uint128' } } },
+      } as TypedAbiFunction<[], Response<boolean, bigint>>,
       verifyBondRolloverWindow: {
         name: 'verify-bond-rollover-window',
         access: 'private',
@@ -4697,7 +4733,7 @@ export const contracts = {
                   { name: 'rewards-per-token', type: 'uint128' },
                 ],
               },
-              error: 'none',
+              error: 'uint128',
             },
           },
         },
@@ -4712,7 +4748,7 @@ export const contracts = {
             earned: bigint;
             rewardsPerToken: bigint;
           },
-          null
+          bigint
         >
       >,
       disallowContractCaller: {
@@ -7068,6 +7104,16 @@ export const contracts = {
         },
         access: 'constant',
       } as TypedAbiVariable<Response<null, bigint>>,
+      ERR_REENTRANT_CALL: {
+        name: 'ERR_REENTRANT_CALL',
+        type: {
+          response: {
+            ok: 'none',
+            error: 'uint128',
+          },
+        },
+        access: 'constant',
+      } as TypedAbiVariable<Response<null, bigint>>,
       ERR_ROLLOVER_TOO_EARLY: {
         name: 'ERR_ROLLOVER_TOO_EARLY',
         type: {
@@ -7317,6 +7363,11 @@ export const contracts = {
         type: 'uint128',
         access: 'variable',
       } as TypedAbiVariable<bigint>,
+      signerManagerCallActive: {
+        name: 'signer-manager-call-active',
+        type: 'bool',
+        access: 'variable',
+      } as TypedAbiVariable<boolean>,
       totalSbtcStaked: {
         name: 'total-sbtc-staked',
         type: 'uint128',
@@ -7446,6 +7497,10 @@ export const contracts = {
         isOk: false,
         value: 39n,
       },
+      ERR_REENTRANT_CALL: {
+        isOk: false,
+        value: 49n,
+      },
       ERR_ROLLOVER_TOO_EARLY: {
         isOk: false,
         value: 48n,
@@ -7516,6 +7571,7 @@ export const contracts = {
       poxPrepareCycleLength: 50n,
       poxRewardCycleLength: 1_050n,
       reserveBalance: 0n,
+      signerManagerCallActive: false,
       totalSbtcStaked: 0n,
     },
     non_fungible_tokens: [],
```

### contrib/core-contract-tests/tests/pox-5/pox-5-reentrancy.test.ts
```diff
@@ -0,0 +1,126 @@
+import { contractFactory, err } from '@clarigen/core';
+import { accounts, project } from '../clarigen-types';
+import { beforeEach, expect, test } from 'vitest';
+import { rov, txErr, txOk } from '@clarigen/test';
+import { secp256k1 } from '@noble/curves/secp256k1.js';
+import { stxToUStx } from '../test-helpers';
+import {
+  deployer,
+  errorCodes,
+  initPox5,
+  pox5,
+  registerSigner,
+  sbtcBalance,
+  signSignerKeyGrant,
+  testSigner,
+} from './pox-5-helpers';
+
+const alice = accounts.wallet_1.address;
+
+const aliceSbtc = 100000n;
+const aliceUstx = stxToUStx(50_000);
+
+beforeEach(() => {
+  initPox5();
+});
+
+/**
+ * A malicious signer whose validate-stake! re-enters pox-5 by calling
+ * unstake-sbtc while the reentrancy guard is active. The guard should
+ * propagate ERR_REENTRANT_CALL back through try!, causing
+ * update-bond-registration to fail entirely with that error code.
+ */
+test('reentrancy via validate-stake! is blocked with ERR_REENTRANT_CALL', () => {
+  const { signer: signer1 } = registerSigner({ caller: deployer });
+  const signer1Name = testSigner.identifier.split('.')[1];
+
+  const maliciousName = 'malicious-validate-signer';
+  const maliciousId = `${deployer}.${maliciousName}`;
+
+  // validate-stake! re-enters pox-5 by calling unstake-sbtc on Alice's
+  // current signer (signer1). The guard is already set, so unstake-sbtc
+  // immediately returns ERR_REENTRANT_CALL, which propagates via try!.
+  const maliciousSource = `\
+(impl-trait .pox-5.signer-manager-trait)
+(use-trait signer-manager-trait .pox-5.signer-manager-trait)
+(define-public (validate-stake!
+    (staker principal) (first-index uint) (num-indexes uint)
+    (amount-ustx uint) (amount-sats uint) (is-bond bool)
+    (signer-calldata (optional (buff 500))))
+  (begin
+    (try! (contract-call? .pox-5 unstake-sbtc .${signer1Name} amount-sats))
+    (ok true)))
+(define-public (checkpoint-staker
+    (staker principal) (first-index uint) (num-indexes uint) (is-bond bool))
+  (ok true))
+(define-public (register-self
+    (signer-manager <signer-manager-trait>) (signer-key (buff 33))
+    (auth-id uint) (signer-sig (buff 65)))
+  (as-contract? ()
+    (try! (contract-call? .pox-5 grant-signer-key signer-key current-contract auth-id signer-sig))
+    (try! (contract-call? .pox-5 register-signer signer-manager signer-key))))`;
+
+  simnet.deployContract(maliciousName, maliciousSource, { clarityVersion: 4 }, deployer);
+
+  const maliciousSk = secp256k1.utils.randomSecretKey();
+  const maliciousKey = secp256k1.getPublicKey(maliciousSk, true);
+  const maliciousAuthId = 9001n;
+  const maliciousSig = signSignerKeyGrant({
+    signerManager: maliciousId,
+    authId: maliciousAuthId,
+    signerSk: maliciousSk,
+  });
+  const maliciousContract = contractFactory(project.contracts.testPox5Signer, maliciousId);
+  txOk(
+    maliciousContract.registerSelf({
+      signerKey: maliciousKey,
+      signerManager: maliciousId,
+      authId: maliciousAuthId,
+      signerSig: maliciousSig,
+    }),
+    deployer,
+  );
+
+  txOk(
+    pox5.setupBond({
+      bondIndex: 0n,
+      targetRate: 1200n,
+      stxValueRatio: 10n,
+      minUstxRatio: 100n,
+      earlyUnlockBytes: new Uint8Array(),
+      earlyUnlockAdmin: deployer,
+      allowlist: [{ maxSats: aliceSbtc, staker: alice }],
+    }),
+    deployer,
+  );
+  txOk(
+    pox5.registerForBond({
+      bondIndex: 0n,
+      signerManager: signer1,
+      amountUstx: aliceUstx,
+      btcLockup: err(aliceSbtc),
+      signerCalldata: null,
+    }),
+    alice,
+  );
+
+  // Alice pre-authorizes maliciousId so check-caller-allowed passes inside
+  // unstake-sbtc, letting execution reach the reentrancy guard.
+  txOk(pox5.allowContractCaller(maliciousId, BigInt(simnet.burnBlockHeight + 10)), alice);
+
+  const aliceBalanceLocked = sbtcBalance(alice);
+
+  const result = txErr(
+    pox5.updateBondRegistration({
+      signerManager: maliciousId,
+      signerCalldata: null,
+      oldSignerManager: signer1,
+    }),
+    alice,
+  );
+
+  expect(result.value).toBe(errorCodes.ERR_REENTRANT_CALL);
+  // sBTC remains locked; Alice's balance is unchanged (not drained).
+  expect(sbtcBalance(alice)).toBe(aliceBalanceLocked);
+  expect(rov(pox5.getTotalSbtcStaked())).toBe(aliceSbtc);
+});
```

### stackslib/src/chainstate/stacks/boot/pox-5.clar
```diff
@@ -60,6 +60,8 @@
 (define-constant ERR_STAKE_IN_PREPARE_PHASE (err u47))
 ;; A staker tried to rollover a bond too early
 (define-constant ERR_ROLLOVER_TOO_EARLY (err u48))
+;; A reentrant call into pox-5 was detected while a signer-manager call was in flight
+(define-constant ERR_REENTRANT_CALL (err u49))
 
 ;; The length, in terms of staking cycles, of a given
 ;; bond period
@@ -370,6 +372,9 @@
 ;; The total amount of sBTC staked
 (define-data-var total-sbtc-staked uint u0)
 
+;; Reentrancy guard: prevents cross-function re-entry through signer-manager trait calls
+(define-data-var signer-manager-call-active bool false)
+
 (define-trait signer-manager-trait (
     (validate-stake!
         ;; staker, first-index, num-indexes, amount-ustx, amount-sats, is-bond, signer-calldata
@@ -378,6 +383,35 @@
     )
 ))
 
+(define-private (validate-no-reentrancy)
+    (ok (asserts! (not (var-get signer-manager-call-active)) ERR_REENTRANT_CALL))
+)
+
+;; A helper function to call the `validate-stake!` function on a given
+;; signer-manager, wrapping the reentrancy guard logic around it. This should
+;; be the only way that `validate-stake!` is called in the contract, since it
+;; is critical to ensure that reentrancy attacks are prevented.
+(define-private (signer-manager-validate-stake
+        (signer-manager <signer-manager-trait>)
+        (staker principal)
+        (first-index uint)
+        (num-indexes uint)
+        (amount-ustx uint)
+        (amount-sats uint)
+        (is-bond bool)
+        (signer-calldata (optional (buff 500)))
+    )
+    (begin
+        (asserts! (not (var-get signer-manager-call-active)) ERR_REENTRANT_CALL)
+        (var-set signer-manager-call-active true)
+        (try! (contract-call? signer-manager validate-stake! staker first-index
+            num-indexes amount-ustx amount-sats is-bond signer-calldata
+        ))
+        (var-set signer-manager-call-active false)
+        (ok true)
+    )
+)
+
 ;; This function can only be called once, when it boots up
 (define-public (set-burnchain-parameters
         (first-burn-height uint)
@@ -404,6 +438,8 @@
     (let ((old-admin (var-get bond-admin)))
         ;; only bond admin can call this.
         (asserts! (is-eq contract-caller old-admin) ERR_UNAUTHORIZED)
+        ;; ensure no reentrancy through signer-manager trait calls
+        (try! (validate-no-reentrancy))
         (var-set bond-admin new-admin)
         (ok {
             old-admin: old-admin,
@@ -449,6 +485,9 @@
         ;; only bond admin can call this.
         (asserts! (is-eq contract-caller (var-get bond-admin)) ERR_UNAUTHORIZED)
 
+        ;; ensure no reentrancy through signer-manager trait calls
+        (try! (validate-no-reentrancy))
+
         ;; only can be called within 2 cycles of bond start
         (asserts!
             (or
@@ -665,7 +704,7 @@
         (asserts! (>= total-balance amount-ustx) ERR_INSUFFICIENT_STX)
 
         ;; Validate that the staker can join this signer
-        (try! (contract-call? signer-manager validate-stake! tx-sender bond-index u1
+        (try! (signer-manager-validate-stake signer-manager tx-sender bond-index u1
             amount-ustx sats-total true signer-calldata
         ))
 
@@ -805,7 +844,7 @@
         (asserts! (not (is-eq signer old-signer)) ERR_UPDATE_BOND_SAME_SIGNER)
 
         ;; Validate that the staker can join this signer
-        (try! (contract-call? signer-manager validate-stake! tx-sender bond-index u1
+        (try! (signer-manager-validate-stake signer-manager tx-sender bond-index u1
             (get amount-ustx current-membership) amount-sats true
             signer-calldata
         ))
@@ -894,6 +933,9 @@
         (signer-key (buff 33))
     )
     (let ((signer (contract-of signer-manager)))
+        ;; ensure no reentrancy through signer-manager trait calls
+        (try! (validate-no-reentrancy))
+
         ;; Because signers can have members register at any time,
         ;; they must use signer key grants instead of per-tx
         ;; authorizations.
@@ -942,7 +984,7 @@
         (try! (verify-not-prepare-phase))
 
         ;; Validate that the staker can join this signer
-        (try! (contract-call? signer-manager validate-stake! tx-sender
+        (try! (signer-manager-validate-stake signer-manager tx-sender
             first-reward-cycle num-cycles amount-ustx u0 false
             signer-calldata
         ))
@@ -1056,7 +1098,7 @@
         (try! (verify-not-prepare-phase))
 
         ;; Validate that the staker can join this signer
-        (try! (contract-call? signer-manager validate-stake! tx-sender
+        (try! (signer-manager-validate-stake signer-manager tx-sender
             first-reward-cycle num-cycles new-lock-amount u0 false
             signer-calldata
         ))
@@ -1131,6 +1173,9 @@
             (current-total-shares (get-total-shares-staked-for-cycle true bond-index))
             (current-shares (get-signer-shares-staked-for-cycle signer true bond-index))
         )
+        ;; ensure no reentrancy through signer-manager trait calls
+        (try! (validate-no-reentrancy))
+
         ;; Only the early unlock admin for this bond period can call this function.
         ;; Calling via other contracts is not allowed.
         (asserts!
@@ -1212,6 +1257,9 @@
         ;;  must be called directly by the tx-sender or by an allowed contract-caller
         (try! (check-caller-allowed))
 
+        ;; ensure no reentrancy through signer-manager trait calls
+        (try! (validate-no-reentrancy))
+
         ;; Take a snapshot of the staker's and signer's current rewards
         (settle-rewards signer true bond-index)
         (settle-staker-rewards signer true bond-index tx-sender)
@@ -1285,6 +1333,9 @@
             ERR_UNSTAKE_IN_PREPARE_PHASE
         )
 
+        ;; ensure no reentrancy through signer-manager trait calls
+        (try! (validate-no-reentrancy))
+
         ;; Remove the staker from all existing cycles
         (try! (remove-staker-from-cycles tx-sender (+ u1 current-cycle)
             (- prev-unlock-cycle current-cycle u1) true
@@ -1806,6 +1857,9 @@
             (cur-reserve (var-get reserve-balance))
             (accrued-rewards (get-new-rewards))
         )
+        ;; ensure no reentrancy through signer-manager trait calls
+        (try! (validate-no-reentrancy))
+
         ;; verify that we are able to compute here
         (asserts! (> calculation-height last-calc)
             ERR_DISTRIBUTION_ALREADY_COMPUTED
@@ -2038,6 +2092,9 @@
             (total-rewards (+ (get earned stx-rewards) bond-totals))
             (prev-accrued-rewards (var-get last-accounted-rewards-only))
         )
+        ;; ensure no reentrancy through signer-manager trait calls
+        (try! (validate-no-reentrancy))
+
         (asserts! (> total-rewards u0) ERR_NO_CLAIMABLE_REWARDS)
         (try! (as-contract?
             ((with-ft 'SM3VDXK3WZZSA84XXFKAFAF15NNZX32CTSG82JFQ4.sbtc-token
@@ -2074,6 +2131,8 @@
         (index uint)
     )
     (let ((rewards-info (settle-staker-rewards contract-caller is-bond index staker)))
+        ;; ensure no reentrancy through signer-manager trait calls
+        (try! (validate-no-reentrancy))
         (map-set staker-unclaimed-rewards-for-cycle {
             is-bond: is-bond,
             index: index,
@@ -2306,6 +2365,9 @@
         (signer-sig (buff 65))
     )
     (begin
+        ;; ensure no reentrancy through signer-manager trait calls
+        (try! (validate-no-reentrancy))
+
         ;; Only the signer contract itself can call this function to grant a signer key
         (asserts! (is-eq contract-caller signer-manager) ERR_UNAUTHORIZED_SIGNER_REGISTRATION)
         (asserts!
@@ -2373,6 +2435,9 @@
         (signer-key (buff 33))
     )
     (begin
+        ;; ensure no reentrancy through signer-manager trait calls
+        (try! (validate-no-reentrancy))
+
         ;; Validate that `tx-sender` has the same pubkey hash as `signer-key`
         (asserts!
             (is-eq
@@ -2898,6 +2963,9 @@
 ;; Revoke contract-caller authorization to call stacking methods
 (define-public (disallow-contract-caller (caller principal))
     (begin
+        ;; ensure no reentrancy through signer-manager trait calls
+        (try! (validate-no-reentrancy))
+
         (asserts! (is-eq tx-sender contract-caller) ERR_UNAUTHORIZED_CALLER)
         (ok (map-delete allowance-contract-callers {
             sender: tx-sender,
@@ -2915,6 +2983,9 @@
         (until-burn-ht (optional uint))
     )
     (begin
+        ;; ensure no reentrancy through signer-manager trait calls
+        (try! (validate-no-reentrancy))
+
         (asserts! (is-eq tx-sender contract-caller) ERR_UNAUTHORIZED_CALLER)
         (ok (map-set allowance-contract-callers {
             sender: tx-sender,
```
