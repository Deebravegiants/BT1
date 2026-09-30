# [?] Allow user provided signature set accounts to prevent DoS

## Summary
Severity: Unknown
Chain: Wormhole
Component: wormhole-foundation/wormhole
Published: 2021-07-26
Source: https://github.com/wormhole-foundation/wormhole/commit/42c3040de1a9faf3f1957e23f56d075cbe2c0347
Type: security-commit

## Details
Allow user provided signature set accounts to prevent DoS

With derived signature set accounts, an old guardian set could frontrun the creation of the account. Since the hash is persisted in the account, we don't need to encode it in the account address.

Change-Id: I49ca46611eb587c8234ac9b2c459263a2ace4219

## Patch
### solana/bridge/agent/src/main.rs
```diff
@@ -130,11 +130,11 @@ impl Agent for AgentImpl {
                 payload: vaa.payload.clone(),
             };
 
-            let verify_txs =
+            let (verify_txs, signature_set) =
                 pack_sig_verification_txs(&rpc, &bridge, &post_data, &vaa.signatures, &key)?;
 
             // Strip signatures
-            let ix = post_vaa(bridge, key.pubkey(), post_data);
+            let ix = post_vaa(bridge, key.pubkey(), signature_set, post_data);
 
             for mut tx in verify_txs {
                 match sign_and_send(&rpc, &mut tx, vec![&key], request.get_ref().skip_preflight) {
@@ -204,7 +204,8 @@ fn pack_sig_verification_txs<'a>(
     vaa: &PostVAAData,
     signatures: &Vec<service::Signature>,
     sender_keypair: &'a Keypair,
-) -> Result<Vec<Transaction>, Status> {
+) -> Result<(Vec<Transaction>, Pubkey), Status> {
+    let signature_set = Keypair::new();
     // Load guardian set
     let guardian_key = GuardianSet::<'_, { AccountState::Initialized }>::key(
         &GuardianSetDerivationData {
@@ -293,7 +294,7 @@ fn pack_sig_verification_txs<'a>(
             *bridge,
             sender_keypair.pubkey(),
             vaa.guardian_set_index,
-            body_hash,
+            signature_set.pubkey(),
             payload,
         ) {
             Ok(v) => v,
@@ -311,7 +312,7 @@ fn pack_sig_verification_txs<'a>(
         ))
     }
 
-    Ok(verify_txs)
+    Ok((verify_txs, signature_set.pubkey()))
 }
 
 fn sign_and_send(
```

### solana/bridge/program/src/accounts.rs
```diff
@@ -55,18 +55,6 @@ impl<'b, const State: AccountState> Seeded<&ClaimDerivationData> for Claim<'b, {
 
 pub type SignatureSet<'b, const State: AccountState> = Data<'b, types::SignatureSet, { State }>;
 
-pub struct SignatureSetDerivationData {
-    pub hash: [u8; 32],
-}
-
-impl<'b, const State: AccountState> Seeded<&SignatureSetDerivationData>
-    for SignatureSet<'b, { State }>
-{
-    fn seeds(data: &SignatureSetDerivationData) -> Vec<Vec<u8>> {
-        vec![data.hash.to_vec()]
-    }
-}
-
 pub type Message<'b, const State: AccountState> = Data<'b, PostedMessage, { State }>;
 
 pub struct MessageDerivationData {
```

### solana/bridge/program/src/api/governance.rs
```diff
@@ -3,8 +3,10 @@ use solitaire::*;
 use solana_program::{
     program::invoke_signed,
     pubkey::Pubkey,
-    sysvar::rent::Rent,
-    sysvar::clock::Clock,
+    sysvar::{
+        clock::Clock,
+        rent::Rent,
+    },
 };
 use solitaire::{
     processors::seeded::Seeded,
```

### solana/bridge/program/src/api/post_vaa.rs
```diff
@@ -17,7 +17,6 @@ use crate::{
         Message,
         MessageDerivationData,
         SignatureSet,
-        SignatureSetDerivationData,
     },
     error::Error::{
         GuardianSetMismatch,
@@ -44,14 +43,6 @@ use std::io::{
     Write,
 };
 
-impl<'a> From<&PostVAA<'a>> for SignatureSetDerivationData {
-    fn from(accs: &PostVAA<'a>) -> Self {
-        SignatureSetDerivationData {
-            hash: accs.signature_set.hash,
-        }
-    }
-}
-
 impl From<&PostVAAData> for GuardianSetDerivationData {
     fn from(data: &PostVAAData) -> Self {
         GuardianSetDerivationData {
@@ -82,9 +73,7 @@ pub struct PostVAA<'b> {
 }
 
 impl<'b> InstructionContext<'b> for PostVAA<'b> {
-    fn verify(&self, program_id: &Pubkey) -> Result<()> {
-        self.signature_set
-            .verify_derivation(program_id, &self.into())?;
+    fn verify(&self, _program_id: &Pubkey) -> Result<()> {
         Ok(())
     }
 }
```

### solana/bridge/program/src/api/verify_signature.rs
```diff
@@ -5,7 +5,6 @@ use crate::{
         GuardianSet,
         GuardianSetDerivationData,
         SignatureSet,
-        SignatureSetDerivationData,
     },
     error::Error::{
         GuardianSetMismatch,
@@ -31,7 +30,7 @@ pub struct VerifySignatures<'b> {
     pub guardian_set: GuardianSet<'b, { AccountState::Initialized }>,
 
     /// Signature Account
-    pub signature_set: Mut<SignatureSet<'b, { AccountState::MaybeInitialized }>>,
+    pub signature_set: Mut<Signer<SignatureSet<'b, { AccountState::MaybeInitialized }>>>,
 
     /// Instruction reflection account (special sysvar)
     pub instruction_acc: Info<'b>,
@@ -48,12 +47,6 @@ impl From<&VerifySignatures<'_>> for GuardianSetDerivationData {
     }
 }
 
-impl From<[u8; 32]> for SignatureSetDerivationData {
-    fn from(hash: [u8; 32]) -> Self {
-        SignatureSetDerivationData { hash }
-    }
-}
-
 #[derive(Default, BorshSerialize, BorshDeserialize)]
 pub struct VerifySignaturesData {
     /// instruction indices of signers (-1 for missing)
@@ -182,17 +175,20 @@ pub fn verify_signatures(
     let mut msg_hash: [u8; 32] = [0u8; 32];
     msg_hash.copy_from_slice(message);
 
-    // Confirm at this point that the derivation succeeds, we didn't have a signature set with the
-    // correct hash until this point.
-    accs.signature_set
-        .verify_derivation(ctx.program_id, &msg_hash.into())?;
-
     if !accs.signature_set.is_initialized() {
         accs.signature_set.signatures = vec![[0u8; 65]; 19];
         accs.signature_set.guardian_set_index = accs.guardian_set.index;
         accs.signature_set.hash = msg_hash;
-        accs.signature_set
-            .create(&msg_hash.into(), ctx, accs.payer.key, Exempt)?;
+
+        let size = accs.signature_set.size();
+        let ix = solana_program::system_instruction::create_account(
+            accs.payer.key,
+            accs.signature_set.info().key,
+            Exempt.amount(size),
+            size as u64,
+            ctx.program_id,
+        );
+        solana_program::program::invoke(&ix, ctx.accounts)?;
     } else {
         // If the account already existed, check that the parameters match
         if accs.signature_set.guardian_set_index != accs.guardian_set.index {
```

### solana/bridge/program/src/instructions.rs
```diff
@@ -1,4 +1,3 @@
-use std::str::FromStr;
 use borsh::BorshSerialize;
 use solana_program::{
     instruction::{
@@ -8,6 +7,7 @@ use solana_program::{
     pubkey::Pubkey,
     sysvar,
 };
+use std::str::FromStr;
 
 use solitaire::{
     processors::seeded::Seeded,
@@ -27,7 +27,6 @@ use crate::{
         Sequence,
         SequenceDerivationData,
         SignatureSet,
-        SignatureSetDerivationData,
     },
     types::ConsistencyLevel,
     InitializeData,
@@ -140,7 +139,7 @@ pub fn verify_signatures(
     program_id: Pubkey,
     payer: Pubkey,
     guardian_set_index: u32,
-    hash: [u8; 32],
+    signature_set: Pubkey,
     data: VerifySignaturesData,
 ) -> solitaire::Result<Instruction> {
     let guardian_set = GuardianSet::<'_, { AccountState::Uninitialized }>::key(
@@ -150,18 +149,13 @@ pub fn verify_signatures(
         &program_id,
     );
 
-    let signature_set = SignatureSet::<'_, { AccountState::Uninitialized }>::key(
-        &SignatureSetDerivationData { hash },
-        &program_id,
-    );
-
     Ok(Instruction {
         program_id,
 
         accounts: vec![
             AccountMeta::new(payer, true),
             AccountMeta::new_readonly(guardian_set, false),
-            AccountMeta::new(signature_set, false),
+            AccountMeta::new(signature_set, true),
             AccountMeta::new_readonly(sysvar::instructions::id(), false),
             AccountMeta::new_readonly(sysvar::rent::id(), false),
             AccountMeta::new_readonly(solana_program::system_program::id(), false),
@@ -171,7 +165,12 @@ pub fn verify_signatures(
     })
 }
 
-pub fn post_vaa(program_id: Pubkey, payer: Pubkey, vaa: PostVAAData) -> Instruction {
+pub fn post_vaa(
+    program_id: Pubkey,
+    payer: Pubkey,
+    signature_set: Pubkey,
+    vaa: PostVAAData,
+) -> Instruction {
     let bridge = Bridge::<'_, { AccountState::Uninitialized }>::key(None, &program_id);
     let guardian_set = GuardianSet::<'_, { AccountState::Uninitialized }>::key(
         &GuardianSetDerivationData {
@@ -180,13 +179,6 @@ pub fn post_vaa(program_id: Pubkey, payer: Pubkey, vaa: PostVAAData) -> Instruct
         &program_id,
     );
 
-    let signature_set = SignatureSet::<'_, { AccountState::Uninitialized }>::key(
-        &SignatureSetDerivationData {
-            hash: hash_vaa(&vaa),
-        },
-        &program_id,
-    );
-
     let mut msg_derivation_data = MessageDerivationData {
         emitter_key: vaa.emitter_address,
         emitter_chain: vaa.emitter_chain,
```

### solana/bridge/program/src/types.rs
```diff
@@ -1,9 +1,9 @@
 use crate::{
     api::ForeignAddress,
     vaa::{
-        SerializeGovernancePayload,
         DeserializeGovernancePayload,
         DeserializePayload,
+        SerializeGovernancePayload,
         SerializePayload,
     },
 };
```

### solana/bridge/program/tests/common.rs
```diff
@@ -69,7 +69,6 @@ use bridge::{
         Sequence,
         SequenceDerivationData,
         SignatureSet,
-        SignatureSetDerivationData,
     },
     instruction,
     instructions,
@@ -323,7 +322,9 @@ mod helpers {
         body: [u8; 32],
         secret_keys: &[SecretKey],
         guardian_set_version: u32,
-    ) -> Result<(), ClientError> {
+    ) -> Result<Pubkey, ClientError> {
+        let signature_set = Keypair::new();
+        let tx_signers = &[payer, &signature_set];
         // Push Secp256k1 instructions for each signature we want to verify.
         for (i, key) in secret_keys.iter().enumerate() {
             // Set this signers signature position as present at 0.
@@ -333,35 +334,41 @@ mod helpers {
             execute(
                 client,
                 payer,
-                &[payer],
+                tx_signers,
                 &vec![
                     new_secp256k1_instruction(&key, &body),
                     instructions::verify_signatures(
                         *program,
                         payer.pubkey(),
                         guardian_set_version,
-                        body,
+                        signature_set.pubkey(),
                         VerifySignaturesData { signers },
                     )
                     .unwrap(),
                 ],
                 CommitmentConfig::processed(),
             )?;
         }
-        Ok(())
+        Ok(signature_set.pubkey())
     }
 
     pub fn post_vaa(
         client: &RpcClient,
         program: &Pubkey,
         payer: &Keypair,
+        signature_set: Pubkey,
         vaa: PostVAAData,
     ) -> Result<Signature, ClientError> {
         execute(
             client,
             payer,
             &[payer],
-            &[instructions::post_vaa(*program, payer.pubkey(), vaa)],
+            &[instructions::post_vaa(
+                *program,
+                payer.pubkey(),
+                signature_set,
+                vaa,
+            )],
             CommitmentConfig::processed(),
         )
     }
```

### solana/bridge/program/tests/integration.rs
```diff
@@ -63,7 +63,6 @@ use bridge::{
         Message,
         MessageDerivationData,
         SignatureSet,
-        SignatureSetDerivationData,
     },
     instruction,
     types::{
@@ -213,16 +212,11 @@ fn test_bridge_messages(context: &mut Context) {
 
         // Emulate Guardian behaviour, verifying the data and publishing signatures/VAA.
         let (vaa, body, body_hash) = common::generate_vaa(&emitter, message.clone(), nonce, 0, 1);
-        common::verify_signatures(client, program, payer, body, &context.secret, 0).unwrap();
-        common::post_vaa(client, program, payer, vaa).unwrap();
+        let signature_set =
+            common::verify_signatures(client, program, payer, body, &context.secret, 0).unwrap();
+        common::post_vaa(client, program, payer, signature_set, vaa).unwrap();
         common::sync(client, payer);
 
-        // Derive where we expect created accounts to be.
-        let signature_set = SignatureSet::<'_, { AccountState::Uninitialized }>::key(
-            &SignatureSetDerivationData { hash: body },
-            &program,
-        );
-
         // Fetch chain accounts to verify state.
         let posted_message: PostedMessage = common::get_account_data(client, &message_key);
         let signatures: SignatureSetData = common::get_account_data(client, &signature_set);
@@ -277,16 +271,11 @@ fn test_bridge_messages(context: &mut Context) {
 
     // Emulate Guardian behaviour, verifying the data and publishing signatures/VAA.
     let (vaa, body, body_hash) = common::generate_vaa(&emitter, message.clone(), nonce, 0, 1);
-    common::verify_signatures(client, program, payer, body, &context.secret, 0).unwrap();
-    common::post_vaa(client, program, payer, vaa).unwrap();
+    let signature_set =
+        common::verify_signatures(client, program, payer, body, &context.secret, 0).unwrap();
+    common::post_vaa(client, program, payer, signature_set, vaa).unwrap();
     common::sync(client, payer);
 
-    // Derive where we expect created accounts to be.
-    let signature_set = SignatureSet::<'_, { AccountState::Uninitialized }>::key(
-        &SignatureSetDerivationData { hash: body },
-        &program,
-    );
-
     // Fetch chain accounts to verify state.
     let posted_message: PostedMessage = common::get_account_data(client, &message_key);
     let signatures: SignatureSetData = common::get_account_data(client, &signature_set);
@@ -412,6 +401,7 @@ fn test_guardian_set_change(context: &mut Context) {
 
     let nonce = rand::thread_rng().gen();
     let emitter = Keypair::from_bytes(&GOVERNANCE_KEY).unwrap();
+    println!("{}", emitter.pubkey().to_string());
     let sequence = context.seq.next(emitter.pubkey().to_bytes());
     let message = GovernancePayloadGuardianSetChange {
         new_guardian_set_index: 1,
@@ -432,8 +422,9 @@ fn test_guardian_set_change(context: &mut Context) {
     .unwrap();
 
     let (vaa, body, body_hash) = common::generate_vaa(&emitter, message.clone(), nonce, 0, 1);
-    common::verify_signatures(client, program, payer, body, &context.secret, 0).unwrap();
-    common::post_vaa(client, program, payer, vaa).unwrap();
+    let signature_set =
+        common::verify_signatures(client, program, payer, body, &context.secret, 0).unwrap();
+    common::post_vaa(client, program, payer, signature_set, vaa).unwrap();
     common::upgrade_guardian_set(
         client,
         program,
@@ -487,16 +478,11 @@ fn test_guardian_set_change(context: &mut Context) {
     // Emulate Guardian behaviour, verifying the data and publishing signatures/VAA.
     let sequence = context.seq.next(emitter.pubkey().to_bytes());
     let (vaa, body, body_hash) = common::generate_vaa(&emitter, message.clone(), nonce, 1, 1);
-    common::verify_signatures(client, program, payer, body, &context.secret, 1).unwrap();
-    common::post_vaa(client, program, payer, vaa).unwrap();
+    let signature_set =
+        common::verify_signatures(client, program, payer, body, &context.secret, 1).unwrap();
+    common::post_vaa(client, program, payer, signature_set, vaa).unwrap();
     common::sync(client, payer);
 
-    // Derive where we expect created accounts to be.
-    let signature_set = SignatureSet::<'_, { AccountState::Uninitialized }>::key(
-        &SignatureSetDerivationData { hash: body },
-        &program,
-    );
-
     // Fetch chain accounts to verify state.
     let posted_message: PostedMessage = common::get_account_data(client, &message_key);
     let signatures: SignatureSetData = common::get_account_data(client, &signature_set);
@@ -600,8 +586,9 @@ fn test_set_fees(context: &mut Context) {
     .unwrap();
 
     let (vaa, body, body_hash) = common::generate_vaa(&emitter, message.clone(), nonce, 1, 1);
-    common::verify_signatures(client, program, payer, body, &context.secret, 1).unwrap();
-    common::post_vaa(client, program, payer, vaa).unwrap();
+    let signature_set =
+        common::verify_signatures(client, program, payer, body, &context.secret, 1).unwrap();
+    common::post_vaa(client, program, payer, signature_set, vaa).unwrap();
     common::set_fees(
         client,
         program,
@@ -624,16 +611,9 @@ fn test_set_fees(context: &mut Context) {
     let emitter = Keypair::new();
     let nonce = rand::thread_rng().gen();
     let message = [0u8; 32].to_vec();
-    assert!(common::post_message(
-        client,
-        program,
-        payer,
-        &emitter,
-        nonce,
-        message.clone(),
-        50,
-    )
-    .is_err());
+    assert!(
+        common::post_message(client, program, payer, &emitter, nonce, message.clone(), 50).is_err()
+    );
     common::sync(client, payer);
 
     assert_eq!(
@@ -658,8 +638,9 @@ fn test_set_fees(context: &mut Context) {
     .unwrap();
 
     let (vaa, body, body_hash) = common::generate_vaa(&emitter, message.clone(), nonce, 1, 1);
-    common::verify_signatures(client, program, payer, body, &context.secret, 1).unwrap();
-    common::post_vaa(client, program, payer, vaa).unwrap();
+    let signature_set =
+        common::verify_signatures(client, program, payer, body, &context.secret, 1).unwrap();
+    common::post_vaa(client, program, payer, signature_set, vaa).unwrap();
     common::sync(client, payer);
 
     // Verify that the fee collector was paid.
@@ -668,12 +649,6 @@ fn test_set_fees(context: &mut Context) {
         account_balance + 100,
     );
 
-    // Derive where we expect created accounts to be.
-    let signature_set = SignatureSet::<'_, { AccountState::Uninitialized }>::key(
-        &SignatureSetDerivationData { hash: body },
-        &program,
-    );
-
     // And that the new message is on chain.
     let posted_message: PostedMessage = common::get_account_data(client, &message_key);
     let signatures: SignatureSetData = common::get_account_data(client, &signature_set);
@@ -736,8 +711,9 @@ fn test_set_fees_fails(context: &mut Context) {
     .unwrap();
 
     let (vaa, body, body_hash) = common::generate_vaa(&emitter, message.clone(), nonce, 1, 1);
-    common::verify_signatures(client, program, payer, body, &context.secret, 1).unwrap();
-    common::post_vaa(client, program, payer, vaa).unwrap();
+    let signature_set =
+        common::verify_signatures(client, program, payer, body, &context.secret, 1).unwrap();
+    common::post_vaa(client, program, payer, signature_set, vaa).unwrap();
     assert!(common::set_fees(
         client,
         program,
@@ -758,11 +734,9 @@ fn test_free_fees(context: &mut Context) {
 
     // Set Fees to 0.
     let nonce = rand::thread_rng().gen();
-    let message = GovernancePayloadSetMessageFee {
-        fee: U256::from(0),
-    }
-    .try_to_vec()
-    .unwrap();
+    let message = GovernancePayloadSetMessageFee { fee: U256::from(0) }
+        .try_to_vec()
+        .unwrap();
 
     let message_key = common::post_message(
         client,
@@ -776,8 +750,9 @@ fn test_free_fees(context: &mut Context) {
     .unwrap();
 
     let (vaa, body, body_hash) = common::generate_vaa(&emitter, message.clone(), nonce, 1, 1);
-    common::verify_signatures(client, program, payer, body, &context.secret, 1).unwrap();
-    common::post_vaa(client, program, payer, vaa).unwrap();
+    let signature_set =
+        common::verify_signatures(client, program, payer, body, &context.secret, 1).unwrap();
+    common::post_vaa(client, program, payer, signature_set, vaa).unwrap();
     common::set_fees(
         client,
         program,
@@ -801,20 +776,13 @@ fn test_free_fees(context: &mut Context) {
     let sequence = context.seq.next(emitter.pubkey().to_bytes());
     let nonce = rand::thread_rng().gen();
     let message = [0u8; 32].to_vec();
-    let message_key = common::post_message(
-        client,
-        program,
-        payer,
-        &emitter,
-        nonce,
-        message.clone(),
-        0,
-    )
-    .unwrap();
+    let message_key =
+        common::post_message(client, program, payer, &emitter, nonce, message.clone(), 0).unwrap();
 
     let (vaa, body, body_hash) = common::generate_vaa(&emitter, message.clone(), nonce, 1, 1);
-    common::verify_signatures(client, program, payer, body, &context.secret, 1).unwrap();
-    common::post_vaa(client, program, payer, vaa).unwrap();
+    let signature_set =
+        common::verify_signatures(client, program, payer, body, &context.secret, 1).unwrap();
+    common::post_vaa(client, program, payer, signature_set, vaa).unwrap();
     common::sync(client, payer);
 
     // Verify that the fee collector was paid.
@@ -823,12 +791,6 @@ fn test_free_fees(context: &mut Context) {
         account_balance,
     );
 
-    // Derive where we expect created accounts to be.
-    let signature_set = SignatureSet::<'_, { AccountState::Uninitialized }>::key(
-        &SignatureSetDerivationData { hash: body },
-        &program,
-    );
-
     // And that the new message is on chain.
     let posted_message: PostedMessage = common::get_account_data(client, &message_key);
     let signatures: SignatureSetData = common::get_account_data(client, &signature_set);
@@ -895,8 +857,9 @@ fn test_transfer_fees(context: &mut Context) {
     .unwrap();
 
     let (vaa, body, body_hash) = common::generate_vaa(&emitter, message.clone(), nonce, 1, 1);
-    common::verify_signatures(client, program, payer, body, &context.secret, 1).unwrap();
-    common::post_vaa(client, program, payer, vaa).unwrap();
+    let signature_set =
+        common::verify_signatures(client, program, payer, body, &context.secret, 1).unwrap();
+    common::post_vaa(client, program, payer, signature_set, vaa).unwrap();
     common::transfer_fees(
         client,
         program,
@@ -943,8 +906,9 @@ fn test_transfer_fees_fails(context: &mut Context) {
     .unwrap();
 
     let (vaa, body, body_hash) = common::generate_vaa(&emitter, message.clone(), nonce, 1, 1);
-    common::verify_signatures(client, program, payer, body, &context.secret, 1).unwrap();
-    common::post_vaa(client, program, payer, vaa).unwrap();
+    let signature_set =
+        common::verify_signatures(client, program, payer, body, &context.secret, 1).unwrap();
+    common::post_vaa(client, program, payer, signature_set, vaa).unwrap();
 
     assert!(common::transfer_fees(
         client,
@@ -989,8 +953,9 @@ fn test_transfer_too_much(context: &mut Context) {
     .unwrap();
 
     let (vaa, body, body_hash) = common::generate_vaa(&emitter, message.clone(), nonce, 1, 1);
-    common::verify_signatures(client, program, payer, body, &context.secret, 1).unwrap();
-    common::post_vaa(client, program, payer, vaa).unwrap();
+    let signature_set =
+        common::verify_signatures(client, program, payer, body, &context.secret, 1).unwrap();
+    common::post_vaa(client, program, payer, signature_set, vaa).unwrap();
 
     // Should fail to transfer.
     assert!(common::transfer_fees(
@@ -1028,15 +993,11 @@ fn test_foreign_bridge_messages(context: &mut Context) {
         &program,
     );
 
-    common::verify_signatures(client, program, payer, body, &context.secret, 0).unwrap();
-    common::post_vaa(client, program, payer, vaa).unwrap();
+    let signature_set =
+        common::verify_signatures(client, program, payer, body, &context.secret, 0).unwrap();
+    common::post_vaa(client, program, payer, signature_set, vaa).unwrap();
     common::sync(client, payer);
 
-    let signature_set = SignatureSet::<'_, { AccountState::Uninitialized }>::key(
-        &SignatureSetDerivationData { hash: body },
-        &program,
-    );
-
     // Fetch chain accounts to verify state.
     let posted_message: PostedMessage = common::get_account_data(client, &message_key);
     let signatures: SignatureSetData = common::get_account_data(client, &signature_set);
@@ -1105,8 +1066,9 @@ fn test_transfer_total_fails(context: &mut Context) {
     .unwrap();
 
     let (vaa, body, body_hash) = common::generate_vaa(&emitter, message.clone(), nonce, 1, 1);
-    common::verify_signatures(client, program, payer, body, &context.secret, 1).unwrap();
-    common::post_vaa(client, program, payer, vaa).unwrap();
+    let signature_set =
+        common::verify_signatures(client, program, payer, body, &context.secret, 1).unwrap();
+    common::post_vaa(client, program, payer, signature_set, vaa).unwrap();
 
     // Transferring total fees should fail, to prevent the account being de-allocated.
     assert!(common::transfer_fees(
@@ -1160,8 +1122,9 @@ fn test_upgrade_contract(context: &mut Context) {
     .unwrap();
 
     let (vaa, body, body_hash) = common::generate_vaa(&emitter, message.clone(), nonce, 0, 1);
-    common::verify_signatures(client, program, payer, body, &context.secret, 0).unwrap();
-    common::post_vaa(client, program, payer, vaa).unwrap();
+    let signature_set =
+        common::verify_signatures(client, program, payer, body, &context.secret, 0).unwrap();
+    common::post_vaa(client, program, payer, signature_set, vaa).unwrap();
     common::upgrade_contract(
         client,
         program,
```
