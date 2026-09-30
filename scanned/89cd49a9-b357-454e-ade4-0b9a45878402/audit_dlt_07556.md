# [?] token-2022: fix panics due to small buffers (#2824)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana-program-library
Published: 2022-01-28
Source: https://github.com/solana-labs/solana-program-library/commit/8a2d3cc227a0c75f07b0c938ef59d9b338b0ecae
Type: security-commit

## Details
token-2022: fix panics due to small buffers (#2824)

* Add panicking test

* Fix panic

* Add another panicking case

* Fix panic

* Add another panicking case

* Fix panics

* Add another panicking case

* Fix

* Add another case

* Move existing fix outside if clause

* Add some helpful comments

## Patch
### token/program-2022/src/extension/mod.rs
```diff
@@ -77,6 +77,9 @@ fn get_extension_indices<V: Extension>(
     let v_account_type = V::TYPE.get_account_type();
     while start_index < tlv_data.len() {
         let tlv_indices = get_tlv_indices(start_index);
+        if tlv_data.len() <= tlv_indices.value_start {
+            return Err(ProgramError::InvalidAccountData);
+        }
         let extension_type =
             ExtensionType::try_from(&tlv_data[tlv_indices.type_start..tlv_indices.length_start])?;
         let account_type = extension_type.get_account_type();
@@ -108,6 +111,9 @@ fn get_extension_types(tlv_data: &[u8]) -> Result<Vec<ExtensionType>, ProgramErr
     let mut start_index = 0;
     while start_index < tlv_data.len() {
         let tlv_indices = get_tlv_indices(start_index);
+        if tlv_data.len() <= tlv_indices.value_start {
+            return Ok(extension_types);
+        }
         let extension_type =
             ExtensionType::try_from(&tlv_data[tlv_indices.type_start..tlv_indices.length_start])?;
         if extension_type == ExtensionType::Uninitialized {
@@ -130,6 +136,9 @@ fn get_first_extension_type(tlv_data: &[u8]) -> Result<Option<ExtensionType>, Pr
         Ok(None)
     } else {
         let tlv_indices = get_tlv_indices(0);
+        if tlv_data.len() <= tlv_indices.length_start {
+            return Ok(None);
+        }
         let extension_type =
             ExtensionType::try_from(&tlv_data[tlv_indices.type_start..tlv_indices.length_start])?;
         if extension_type == ExtensionType::Uninitialized {
@@ -183,10 +192,13 @@ fn type_and_tlv_indices<S: BaseState>(
     } else {
         let account_type_index = BASE_ACCOUNT_LENGTH.saturating_sub(S::LEN);
         // check padding is all zeroes
+        let tlv_start_index = account_type_index.saturating_add(size_of::<AccountType>());
+        if rest_input.len() <= tlv_start_index {
+            return Err(ProgramError::InvalidAccountData);
+        }
         if rest_input[..account_type_index] != vec![0; account_type_index] {
             Err(ProgramError::InvalidAccountData)
         } else {
-            let tlv_start_index = account_type_index.saturating_add(size_of::<AccountType>());
             Ok(Some((account_type_index, tlv_start_index)))
         }
     }
@@ -201,6 +213,7 @@ fn get_extension<S: BaseState, V: Extension>(tlv_data: &[u8]) -> Result<&V, Prog
         length_start,
         value_start,
     } = get_extension_indices::<V>(tlv_data, false)?;
+    // get_extension_indices has checked that tlv_data is long enough to include these indices
     let length = pod_from_bytes::<Length>(&tlv_data[length_start..value_start])?;
     let value_end = value_start.saturating_add(usize::from(*length));
     pod_from_bytes::<V>(&tlv_data[value_start..value_end])
@@ -223,6 +236,7 @@ impl<S: BaseState> StateWithExtensionsOwned<S> {
         let mut rest = input.split_off(S::LEN);
         let base = S::unpack(&input)?;
         if let Some((account_type_index, tlv_start_index)) = type_and_tlv_indices::<S>(&rest)? {
+            // type_and_tlv_indices() checks that returned indexes are within range
             let account_type = AccountType::try_from(rest[account_type_index])
                 .map_err(|_| ProgramError::InvalidAccountData)?;
             check_account_type::<S>(account_type)?;
@@ -264,6 +278,7 @@ impl<'data, S: BaseState> StateWithExtensions<'data, S> {
         let (base_data, rest) = input.split_at(S::LEN);
         let base = S::unpack(base_data)?;
         if let Some((account_type_index, tlv_start_index)) = type_and_tlv_indices::<S>(rest)? {
+            // type_and_tlv_indices() checks that returned indexes are within range
             let account_type = AccountType::try_from(rest[account_type_index])
                 .map_err(|_| ProgramError::InvalidAccountData)?;
             check_account_type::<S>(account_type)?;
@@ -311,6 +326,7 @@ impl<'data, S: BaseState> StateWithExtensionsMut<'data, S> {
         let (base_data, rest) = input.split_at_mut(S::LEN);
         let base = S::unpack(base_data)?;
         if let Some((account_type_index, tlv_start_index)) = type_and_tlv_indices::<S>(rest)? {
+            // type_and_tlv_indices() checks that returned indexes are within range
             let account_type = AccountType::try_from(rest[account_type_index])
                 .map_err(|_| ProgramError::InvalidAccountData)?;
             check_account_type::<S>(account_type)?;
@@ -342,6 +358,7 @@ impl<'data, S: BaseState> StateWithExtensionsMut<'data, S> {
             return Err(TokenError::AlreadyInUse.into());
         }
         if let Some((account_type_index, tlv_start_index)) = type_and_tlv_indices::<S>(rest)? {
+            // type_and_tlv_indices() checks that returned indexes are within range
             let account_type = AccountType::try_from(rest[account_type_index])
                 .map_err(|_| ProgramError::InvalidAccountData)?;
             if account_type != AccountType::Uninitialized {
@@ -380,6 +397,9 @@ impl<'data, S: BaseState> StateWithExtensionsMut<'data, S> {
             length_start,
             value_start,
         } = get_extension_indices::<V>(self.tlv_data, init)?;
+        if self.tlv_data[type_start..].len() < V::TYPE.get_tlv_len() {
+            return Err(ProgramError::InvalidAccountData);
+        }
         if init {
             // write extension type
             let extension_type_array: [u8; 2] = V::TYPE.into();
@@ -556,19 +576,24 @@ impl ExtensionType {
         }
     }
 
+    /// Get the TLV length for an ExtensionType
+    fn get_tlv_len(&self) -> usize {
+        self.get_type_len()
+            .saturating_add(size_of::<ExtensionType>())
+            .saturating_add(pod_get_packed_len::<Length>())
+    }
+
+    /// Get the TLV length for a set of ExtensionTypes
+    fn get_total_tlv_len(extension_types: &[Self]) -> usize {
+        extension_types.iter().map(|e| e.get_tlv_len()).sum()
+    }
+
     /// Get the required account data length for the given ExtensionTypes
     pub fn get_account_len<S: BaseState>(extension_types: &[Self]) -> usize {
         if extension_types.is_empty() {
             S::LEN
         } else {
-            let extension_size: usize = extension_types
-                .iter()
-                .map(|e| {
-                    e.get_type_len()
-                        .saturating_add(size_of::<ExtensionType>())
-                        .saturating_add(pod_get_packed_len::<Length>())
-                })
-                .sum();
+            let extension_size = Self::get_total_tlv_len(extension_types);
             let account_size = extension_size
                 .saturating_add(BASE_ACCOUNT_LENGTH)
                 .saturating_add(size_of::<AccountType>());
@@ -1293,4 +1318,30 @@ mod test {
         assert_eq!(extension.padding2, [2; 48]);
         assert_eq!(extension.padding3, [3; 9]);
     }
+
+    #[test]
+    fn test_init_buffer_too_small() {
+        let mint_size =
+            ExtensionType::get_account_len::<Mint>(&[ExtensionType::MintCloseAuthority]);
+        let mut buffer = vec![0; mint_size - 1];
+        let mut state = StateWithExtensionsMut::<Mint>::unpack_uninitialized(&mut buffer).unwrap();
+        let err = state.init_extension::<MintCloseAuthority>().unwrap_err();
+        assert_eq!(err, ProgramError::InvalidAccountData);
+
+        state.tlv_data[0] = 3;
+        state.tlv_data[2] = 32;
+        let err = state.get_extension_mut::<MintCloseAuthority>().unwrap_err();
+        assert_eq!(err, ProgramError::InvalidAccountData);
+
+        let mut buffer = vec![0; Mint::LEN + 2];
+        let err = StateWithExtensionsMut::<Mint>::unpack_uninitialized(&mut buffer).unwrap_err();
+        assert_eq!(err, ProgramError::InvalidAccountData);
+
+        let mut buffer = vec![0; BASE_ACCOUNT_LENGTH + 2];
+        let mut state = StateWithExtensionsMut::<Mint>::unpack_uninitialized(&mut buffer).unwrap();
+        let err = state.get_extension_mut::<MintCloseAuthority>().unwrap_err();
+        assert_eq!(err, ProgramError::InvalidAccountData);
+
+        assert_eq!(state.get_extension_types().unwrap(), vec![]);
+    }
 }
```
