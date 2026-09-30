# [?] Fix panic parsing seeds when account has qualified path (#2268)

## Summary
Severity: Unknown
Chain: Solana
Component: otter-sec/anchor
Published: 2022-11-22
Source: https://github.com/otter-sec/anchor/commit/982799b7e6acc3c48764fb8acd6efe9bee6265d8
Type: security-commit

## Details
Fix panic parsing seeds when account has qualified path (#2268)

* Fix panic parsing seeds when account has qualified path

* Add a test for seed derivation with account using type with path

## Patch
### lang/syn/src/lib.rs
```diff
@@ -197,7 +197,7 @@ impl AccountField {
     }
 
     pub fn ty_name(&self) -> Option<String> {
-        match self {
+        let qualified_ty_name = match self {
             AccountField::Field(field) => match &field.ty {
                 Ty::Account(account) => Some(parser::tts_to_string(&account.account_type_path)),
                 Ty::ProgramAccount(account) => {
@@ -206,7 +206,12 @@ impl AccountField {
                 _ => None,
             },
             AccountField::CompositeField(field) => Some(field.symbol.clone()),
-        }
+        };
+
+        qualified_ty_name.map(|name| match name.rsplit_once(" :: ") {
+            Some((_prefix, suffix)) => suffix.to_string(),
+            None => name,
+        })
     }
 }
 
```

### tests/pda-derivation/programs/pda-derivation/src/lib.rs
```diff
@@ -1,6 +1,8 @@
 //! The typescript example serves to show how one would setup an Anchor
 //! workspace with TypeScript tests and migrations.
 
+mod other;
+
 use anchor_lang::prelude::*;
 
 declare_id!("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS");
@@ -22,6 +24,12 @@ pub mod pda_derivation {
         Ok(())
     }
 
+    pub fn init_another(ctx: Context<InitAnotherBase>, data: u64) -> Result<()> {
+        let base = &mut ctx.accounts.base;
+        base.data = data;
+        Ok(())
+    }
+
     pub fn init_my_account(ctx: Context<InitMyAccount>, _seed_a: u8) -> Result<()> {
         ctx.accounts.account.data = 1337;
         Ok(())
@@ -41,10 +49,25 @@ pub struct InitBase<'info> {
     system_program: Program<'info, System>,
 }
 
+#[derive(Accounts)]
+pub struct InitAnotherBase<'info> {
+    #[account(
+        init,
+        payer = payer,
+        space = 8+8,
+    )]
+    base: Account<'info, crate::other::AnotherBaseAccount>,
+    #[account(mut)]
+    payer: Signer<'info>,
+    system_program: Program<'info, System>,
+}
+
 #[derive(Accounts)]
 #[instruction(seed_a: u8)]
 pub struct InitMyAccount<'info> {
     base: Account<'info, BaseAccount>,
+    // Intentionally using this qualified form instead of importing to test parsing
+    another_base: Account<'info, crate::other::AnotherBaseAccount>,
     base2: AccountInfo<'info>,
     #[account(
         init,
@@ -63,6 +86,7 @@ pub struct InitMyAccount<'info> {
             &MY_SEED_U64.to_le_bytes(),
             base.base_data.to_le_bytes().as_ref(),
             base.base_data_key.as_ref(),
+            another_base.data.to_le_bytes().as_ref(),
         ],
         bump,
     )]
```

### tests/pda-derivation/programs/pda-derivation/src/other.rs
```diff
@@ -0,0 +1,6 @@
+use anchor_lang::prelude::*;
+
+#[account]
+pub struct AnotherBaseAccount {
+    pub data: u64,
+}
```

### tests/pda-derivation/tests/typescript.spec.ts
```diff
@@ -15,6 +15,8 @@ describe("typescript", () => {
   const base = Keypair.generate();
   const dataKey = Keypair.generate();
   const data = new BN(1);
+  const another = Keypair.generate();
+  const anotherData = new BN(2);
   const seedA = 4;
 
   it("Inits the base account", async () => {
@@ -25,6 +27,14 @@ describe("typescript", () => {
       })
       .signers([base])
       .rpc();
+
+    await program.methods
+      .initAnother(anotherData)
+      .accounts({
+        base: another.publicKey,
+      })
+      .signers([another])
+      .rpc();
   });
 
   it("Inits the derived accounts", async () => {
@@ -47,13 +57,15 @@ describe("typescript", () => {
         new anchor.BN(MY_SEED_U64).toArrayLike(Buffer, "le", 8),
         new anchor.BN(data).toArrayLike(Buffer, "le", 8),
         dataKey.publicKey.toBuffer(),
+        new anchor.BN(anotherData).toArrayLike(Buffer, "le", 8),
       ],
       program.programId
     )[0];
 
     const tx = program.methods.initMyAccount(seedA).accounts({
       base: base.publicKey,
       base2: base.publicKey,
+      anotherBase: another.publicKey,
     });
 
     const keys = await tx.pubkeys();
@@ -87,6 +99,7 @@ describe("typescript", () => {
       .accounts({
         base: base.publicKey,
         base2: base.publicKey,
+        anotherBase: another.publicKey,
       })
       .pubkeys();
 
```
