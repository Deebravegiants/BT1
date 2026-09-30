# [?] fix(lang): prevent panic on undersized zero-copy account deserialization (#4555)

## Summary
Severity: Unknown
Chain: Solana
Component: coral-xyz/anchor
Published: 2026-05-19
Source: https://github.com/otter-sec/anchor/commit/b05a2192f53e2aae3b0cba1b7a1a2d3ca826c89c
Type: security-commit

## Details
fix(lang): prevent panic on undersized zero-copy account deserialization (#4555)

* fix(lang): enhance account deserialization checks to prevent panics

* test(lang): add tests for AccountLoader handling of truncated accounts

* fix(lang/syn): improve error handling for account deserialization failures

* refactor(lang): extract size check into separate method for improved readability and maintainability

## Patch
### lang/src/accounts/account_loader.rs
```diff
@@ -156,6 +156,17 @@ impl<'info, T: ZeroCopy + Owner> AccountLoader<'info, T> {
         Ok(AccountLoader::new_unchecked(acc_info))
     }
 
+    fn check_size(&self, data: &[u8]) -> Result<()> {
+        let required = T::DISCRIMINATOR
+            .len()
+            .checked_add(mem::size_of::<T>())
+            .ok_or(ErrorCode::AccountDidNotDeserialize)?;
+        if data.len() < required {
+            return Err(ErrorCode::AccountDidNotDeserialize.into());
+        }
+        Ok(())
+    }
+
     /// Returns a Ref to the account data structure for reading.
     pub fn load(&self) -> Result<Ref<'_, T>> {
         let data = self.acc_info.try_borrow_data()?;
@@ -169,6 +180,8 @@ impl<'info, T: ZeroCopy + Owner> AccountLoader<'info, T> {
             return Err(ErrorCode::AccountDiscriminatorMismatch.into());
         }
 
+        self.check_size(&data)?;
+
         Ok(Ref::map(data, |data| {
             bytemuck::from_bytes(&data[disc.len()..mem::size_of::<T>() + disc.len()])
         }))
@@ -193,6 +206,8 @@ impl<'info, T: ZeroCopy + Owner> AccountLoader<'info, T> {
             return Err(ErrorCode::AccountDiscriminatorMismatch.into());
         }
 
+        self.check_size(&data)?;
+
         Ok(RefMut::map(data, |data| {
             bytemuck::from_bytes_mut(
                 &mut data.deref_mut()[disc.len()..mem::size_of::<T>() + disc.len()],
@@ -213,6 +228,8 @@ impl<'info, T: ZeroCopy + Owner> AccountLoader<'info, T> {
 
         // The discriminator should be zero, since we're initializing.
         let disc = T::DISCRIMINATOR;
+        self.check_size(&data)?;
+
         let given_disc = &data[..disc.len()];
         let has_disc = given_disc.iter().any(|b| *b != 0);
         if has_disc {
```

### lang/syn/src/codegen/accounts/constraints.rs
```diff
@@ -276,6 +276,9 @@ pub fn generate_constraint_zeroed(
     quote! {
         let #field: #ty_decl = {
             let mut __data: &[u8] = &#field.try_borrow_data()?;
+            if __data.len() < #discriminator.len() {
+                return Err(anchor_lang::error::Error::from(anchor_lang::error::ErrorCode::AccountDidNotDeserialize).with_account_name(#name_str));
+            }
             let __disc = &__data[..#discriminator.len()];
             let __has_disc = __disc.iter().any(|b| *b != 0);
             if __has_disc {
```

### lang/tests/account_loader_truncation.rs
```diff
@@ -0,0 +1,76 @@
+//! Regression tests proving AccountLoader accessors return structured errors instead of panicking on truncated accounts.
+
+use anchor_lang::{accounts::account_loader::AccountLoader, prelude::*};
+
+declare_id!("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS");
+
+#[account(zero_copy)]
+#[derive(Default, Debug)]
+pub struct ZcStruct {
+    pub data: u64,
+}
+
+macro_rules! setup_truncated_account {
+    ($key:ident, $owner:ident, $lamports:ident, $data:ident, $account_info:ident) => {
+        let $key = Pubkey::new_unique();
+        let $owner = crate::ID;
+        let mut $lamports = 0;
+        let mut $data = ZcStruct::DISCRIMINATOR.to_vec();
+
+        #[allow(unused_variables)]
+        let $account_info = AccountInfo::new(
+            &$key,
+            false,
+            true,
+            &mut $lamports,
+            &mut $data,
+            &$owner,
+            false,
+        );
+    };
+}
+
+#[test]
+fn test_load_truncated() {
+    setup_truncated_account!(key, owner, lamports, data, account_info);
+    let loader: AccountLoader<ZcStruct> = AccountLoader::try_from(&account_info).unwrap();
+    assert_eq!(
+        loader.load().unwrap_err(),
+        ErrorCode::AccountDidNotDeserialize.into()
+    );
+}
+
+#[test]
+fn test_load_mut_truncated() {
+    setup_truncated_account!(key, owner, lamports, data, account_info);
+    let loader: AccountLoader<ZcStruct> = AccountLoader::try_from(&account_info).unwrap();
+    assert_eq!(
+        loader.load_mut().unwrap_err(),
+        ErrorCode::AccountDidNotDeserialize.into()
+    );
+}
+
+#[test]
+fn test_load_init_truncated() {
+    setup_truncated_account!(key, owner, lamports, data, account_info);
+    let loader: AccountLoader<ZcStruct> =
+        AccountLoader::try_from_unchecked(&crate::ID, &account_info).unwrap();
+    assert_eq!(
+        loader.load_init().unwrap_err(),
+        ErrorCode::AccountDidNotDeserialize.into()
+    );
+}
+
+#[test]
+fn test_load_valid_full_size() {
+    let key = Pubkey::new_unique();
+    let owner = crate::ID;
+    let mut lamports = 0;
+    let mut data = vec![0u8; 8 + std::mem::size_of::<ZcStruct>()];
+    data[..8].copy_from_slice(ZcStruct::DISCRIMINATOR);
+
+    let account_info = AccountInfo::new(&key, false, true, &mut lamports, &mut data, &owner, false);
+    let loader: AccountLoader<ZcStruct> = AccountLoader::try_from(&account_info).unwrap();
+
+    assert!(loader.load().is_ok());
+}
```
