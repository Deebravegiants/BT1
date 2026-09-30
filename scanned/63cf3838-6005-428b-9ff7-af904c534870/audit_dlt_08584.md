# [?] Change EnvBase functions to not panic, fix #434 (#458)

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/rs-soroban-env
Published: 2022-09-21
Source: https://github.com/stellar/rs-soroban-env/commit/a1f3a5c6df414afda3d07949b4f88ba5759dfa6e
Type: security-commit

## Details
Change EnvBase functions to not panic, fix #434 (#458)

* Change EnvBase functions to not panic, fix #434

* Regenerate wasms with locally-patched SDK

## Patch
### soroban-env-common/src/array.rs
```diff
@@ -1,25 +1,28 @@
+use crate::xdr::ScHostValErrorCode;
 use stellar_xdr::ScObjectType;
 
 use crate::{
-    ConversionError, Env, EnvVal, IntoVal, Object, RawVal, RawValConvertible, TryFromVal,
-    TryIntoVal,
+    ConversionError, Env, Object, RawVal, RawValConvertible, Status, TryFromVal, TryIntoVal,
 };
 
+// TODO: these conversions happen as RawVal, but they actually take and produce
+// Objects; consider making the signatures tighter.
+
 impl<E: Env, const N: usize> TryFromVal<E, RawVal> for [u8; N] {
-    type Error = ConversionError;
+    type Error = Status;
 
     fn try_from_val(env: &E, val: RawVal) -> Result<Self, Self::Error> {
         if !Object::val_is_obj_type(val, ScObjectType::Bytes) {
-            return Err(ConversionError);
+            return Err(ScHostValErrorCode::UnexpectedValType.into());
         }
         let env = env.clone();
         let bytes = unsafe { Object::unchecked_from_val(val) };
         let len = unsafe { u32::unchecked_from_val(env.bytes_len(bytes)) };
         if len as usize != N {
-            return Err(ConversionError);
+            return Err(ConversionError.into());
         }
         let mut arr = [0u8; N];
-        env.bytes_copy_to_slice(bytes, RawVal::U32_ZERO, &mut arr);
+        env.bytes_copy_to_slice(bytes, RawVal::U32_ZERO, &mut arr)?;
         Ok(arr)
     }
 }
@@ -32,47 +35,36 @@ impl<E: Env, const N: usize> TryIntoVal<E, [u8; N]> for RawVal {
     }
 }
 
-impl<E: Env> IntoVal<E, RawVal> for &[u8] {
-    fn into_val(self, env: &E) -> RawVal {
-        let env = env.clone();
-        let mut bytes = env.bytes_new();
-        bytes = env.bytes_copy_from_slice(bytes, RawVal::U32_ZERO, self);
-        bytes.to_raw()
-    }
-}
-
-impl<E: Env> IntoVal<E, EnvVal<E, RawVal>> for &[u8] {
-    fn into_val(self, env: &E) -> EnvVal<E, RawVal> {
-        let rv: RawVal = self.into_val(env);
-        EnvVal {
-            env: env.clone(),
-            val: rv,
-        }
-    }
-}
-
-impl<E: Env, const N: usize> IntoVal<E, RawVal> for &[u8; N] {
-    fn into_val(self, env: &E) -> RawVal {
-        let slice: &[u8] = self;
-        slice.into_val(env)
+impl<E: Env> TryIntoVal<E, RawVal> for &[u8] {
+    type Error = Status;
+    #[inline(always)]
+    fn try_into_val(self, env: &E) -> Result<RawVal, Self::Error> {
+        Ok(env.bytes_new_from_slice(self)?.to_raw())
     }
 }
 
-impl<E: Env, const N: usize> IntoVal<E, EnvVal<E, RawVal>> for &[u8; N] {
-    fn into_val(self, env: &E) -> EnvVal<E, RawVal> {
-        let slice: &[u8] = self;
-        slice.into_val(env)
+impl<E: Env, const N: usize> TryIntoVal<E, RawVal> for [u8; N] {
+    type Error = Status;
+    #[inline(always)]
+    fn try_into_val(self, env: &E) -> Result<RawVal, Self::Error> {
+        self.as_slice().try_into_val(env)
     }
 }
 
-impl<E: Env, const N: usize> IntoVal<E, RawVal> for [u8; N] {
-    fn into_val(self, env: &E) -> RawVal {
-        (&self).into_val(env)
+#[cfg(feature = "std")]
+impl<E: Env> TryIntoVal<E, RawVal> for Vec<u8> {
+    type Error = Status;
+    #[inline(always)]
+    fn try_into_val(self, env: &E) -> Result<RawVal, Self::Error> {
+        (&self).try_into_val(env)
     }
 }
 
-impl<E: Env, const N: usize> IntoVal<E, EnvVal<E, RawVal>> for [u8; N] {
-    fn into_val(self, env: &E) -> EnvVal<E, RawVal> {
-        (&self).into_val(env)
+#[cfg(feature = "std")]
+impl<E: Env> TryIntoVal<E, RawVal> for &Vec<u8> {
+    type Error = Status;
+    #[inline(always)]
+    fn try_into_val(self, env: &E) -> Result<RawVal, Self::Error> {
+        self.as_slice().try_into_val(env)
     }
 }
```

### soroban-env-common/src/env.rs
```diff
@@ -30,15 +30,16 @@ pub trait EnvBase: Sized + Clone {
 
     /// Copy a slice of bytes from the caller's memory into an existing `Bytes`
     /// object the host, returning a new `Bytes`.
-    fn bytes_copy_from_slice(&self, b: Object, b_pos: RawVal, mem: &[u8]) -> Object;
+    fn bytes_copy_from_slice(&self, b: Object, b_pos: RawVal, mem: &[u8])
+        -> Result<Object, Status>;
 
     /// Copy a slice of bytes from a `Bytes` object in the host into the
     /// caller's memory.
-    fn bytes_copy_to_slice(&self, b: Object, b_pos: RawVal, mem: &mut [u8]);
+    fn bytes_copy_to_slice(&self, b: Object, b_pos: RawVal, mem: &mut [u8]) -> Result<(), Status>;
 
     /// Form a new `Bytes` object in the host from a slice of memory in the
     /// caller.
-    fn bytes_new_from_slice(&self, mem: &[u8]) -> Object;
+    fn bytes_new_from_slice(&self, mem: &[u8]) -> Result<Object, Status>;
 
     // As with the bytes functions above, these take _slices_ with definite
     // lifetimes. The first slice is interpreted as a (very restricted)
@@ -66,25 +67,35 @@ pub trait EnvBase: Sized + Clone {
     /// a simplified format string (supporting only positional `{}` markers) and
     /// a single [RawVal] argument that will be inserted at the marker in the
     /// format string.
-    fn log_static_fmt_val(&self, fmt: &'static str, v: RawVal);
+    fn log_static_fmt_val(&self, fmt: &'static str, v: RawVal) -> Result<(), Status>;
 
     /// Log a formatted debugging message to the debug log (if present), passing
     /// a simplified format string (supporting only positional `{}` markers) and
     /// a single string-slice argument that will be inserted at the marker in
     /// the format string.
-    fn log_static_fmt_static_str(&self, fmt: &'static str, s: &'static str);
+    fn log_static_fmt_static_str(&self, fmt: &'static str, s: &'static str) -> Result<(), Status>;
 
     /// Log a formatted debugging message to the debug log (if present), passing
     /// a simplified format string (supporting only positional `{}` markers) and
     /// both a [RawVal] and a string-slice argument, that will each be inserted
     /// at markers in the format string.
-    fn log_static_fmt_val_static_str(&self, fmt: &'static str, v: RawVal, s: &'static str);
+    fn log_static_fmt_val_static_str(
+        &self,
+        fmt: &'static str,
+        v: RawVal,
+        s: &'static str,
+    ) -> Result<(), Status>;
 
     /// Log a formatted debugging message to the debug log (if present), passing
     /// a simplified format string (supporting only positional `{}` markers) and
     /// both a slice of [RawVal]s and a slice of string-slice argument, that
     /// will be sequentially inserted at markers in the format string.
-    fn log_static_fmt_general(&self, fmt: &'static str, vals: &[RawVal], strs: &[&'static str]);
+    fn log_static_fmt_general(
+        &self,
+        fmt: &'static str,
+        vals: &[RawVal],
+        strs: &[&'static str],
+    ) -> Result<(), Status>;
 }
 
 ///////////////////////////////////////////////////////////////////////////////
```

### soroban-env-common/src/env_val.rs
```diff
@@ -127,7 +127,9 @@ impl<E: Env, V> TryFromVal<E, V> for EnvVal<E, V> {
 }
 
 pub(crate) fn log_err_convert<T>(env: &impl Env, val: &impl AsRef<RawVal>) {
-    env.log_static_fmt_val_static_str(
+    // Logging here is best-effort; ignore failures (they only arise if we're
+    // out of gas or something otherwise-unrecoverable).
+    let _ = env.log_static_fmt_val_static_str(
         "can't convert {} to {}",
         *val.as_ref(),
         core::any::type_name::<T>(),
```

### soroban-env-common/src/meta.rs
```diff
@@ -56,5 +56,5 @@
 // implementations over a long period of time.
 
 soroban_env_macros::generate_env_meta_consts!(
-    interface_version: 14,
+    interface_version: 15,
 );
```

### soroban-env-common/src/str.rs
```diff
@@ -1,12 +1,13 @@
-use core::convert::Infallible;
-
-use crate::{Env, IntoVal, RawVal, TryIntoVal};
+use crate::{ConversionError, Env, RawVal, TryIntoVal};
 
 #[cfg(feature = "std")]
 use stellar_xdr::ScObjectType;
 
 #[cfg(feature = "std")]
-use crate::{ConversionError, Object, RawValConvertible, TryFromVal};
+use crate::{Object, RawValConvertible, TryFromVal};
+
+// TODO: these conversions happen as RawVal, but they actually take and produce
+// Objects; consider making the signatures tighter.
 
 #[cfg(feature = "std")]
 impl<E: Env> TryFromVal<E, RawVal> for String {
@@ -18,7 +19,8 @@ impl<E: Env> TryFromVal<E, RawVal> for String {
         if obj.is_obj_type(ScObjectType::Bytes) {
             let len = unsafe { <u32 as RawValConvertible>::unchecked_from_val(env.bytes_len(obj)) };
             let mut vec = std::vec![0; len as usize];
-            env.bytes_copy_to_slice(obj, RawVal::U32_ZERO, &mut vec);
+            env.bytes_copy_to_slice(obj, RawVal::U32_ZERO, &mut vec)
+                .map_err(|_| ConversionError)?;
             String::from_utf8(vec).map_err(|_| ConversionError)
         } else {
             Err(ConversionError)
@@ -36,51 +38,31 @@ impl<E: Env> TryIntoVal<E, String> for RawVal {
     }
 }
 
-impl<E: Env> IntoVal<E, RawVal> for &str {
-    #[inline(always)]
-    fn into_val(self, env: &E) -> RawVal {
-        env.bytes_new_from_slice(self.as_bytes()).to_raw()
-    }
-}
-
-#[cfg(feature = "std")]
-impl<E: Env> IntoVal<E, RawVal> for String {
-    #[inline(always)]
-    fn into_val(self, env: &E) -> RawVal {
-        <_ as IntoVal<E, RawVal>>::into_val(&self, env)
-    }
-}
-
-#[cfg(feature = "std")]
-impl<E: Env> IntoVal<E, RawVal> for &String {
-    #[inline(always)]
-    fn into_val(self, env: &E) -> RawVal {
-        <&str as IntoVal<E, RawVal>>::into_val(self, env)
-    }
-}
-
 impl<E: Env> TryIntoVal<E, RawVal> for &str {
-    type Error = Infallible;
+    type Error = ConversionError;
     #[inline(always)]
     fn try_into_val(self, env: &E) -> Result<RawVal, Self::Error> {
-        Ok(<_ as IntoVal<E, RawVal>>::into_val(self, env))
+        Ok(env
+            .bytes_new_from_slice(self.as_bytes())
+            .map_err(|_| ConversionError)?
+            .to_raw())
     }
 }
 
 #[cfg(feature = "std")]
 impl<E: Env> TryIntoVal<E, RawVal> for String {
-    type Error = Infallible;
+    type Error = ConversionError;
     #[inline(always)]
     fn try_into_val(self, env: &E) -> Result<RawVal, Self::Error> {
-        Ok(<_ as IntoVal<E, RawVal>>::into_val(self, env))
+        (&self).try_into_val(env)
     }
 }
 
 #[cfg(feature = "std")]
 impl<E: Env> TryIntoVal<E, RawVal> for &String {
-    type Error = Infallible;
+    type Error = ConversionError;
     #[inline(always)]
     fn try_into_val(self, env: &E) -> Result<RawVal, Self::Error> {
-        Ok(<_ as IntoVal<E, RawVal>>::into_val(self, env))
+        self.as_str().try_into_val(env)
     }
 }
```

### soroban-env-common/src/unimplemented_env.rs
```diff
@@ -17,31 +17,55 @@ impl EnvBase for UnimplementedEnv {
         Self
     }
 
-    fn bytes_copy_from_slice(&self, _b: Object, _b_pos: RawVal, _mem: &[u8]) -> Object {
+    fn bytes_copy_from_slice(
+        &self,
+        _b: Object,
+        _b_pos: RawVal,
+        _mem: &[u8],
+    ) -> Result<Object, Status> {
         unimplemented!()
     }
 
-    fn bytes_copy_to_slice(&self, _b: Object, _b_pos: RawVal, _mem: &mut [u8]) {
+    fn bytes_copy_to_slice(
+        &self,
+        _b: Object,
+        _b_pos: RawVal,
+        _mem: &mut [u8],
+    ) -> Result<(), Status> {
         unimplemented!()
     }
 
-    fn bytes_new_from_slice(&self, _mem: &[u8]) -> Object {
+    fn bytes_new_from_slice(&self, _mem: &[u8]) -> Result<Object, Status> {
         unimplemented!()
     }
 
-    fn log_static_fmt_val(&self, _fmt: &'static str, _v: RawVal) {
+    fn log_static_fmt_val(&self, _fmt: &'static str, _v: RawVal) -> Result<(), Status> {
         unimplemented!()
     }
 
-    fn log_static_fmt_static_str(&self, _fmt: &'static str, _s: &'static str) {
+    fn log_static_fmt_static_str(
+        &self,
+        _fmt: &'static str,
+        _s: &'static str,
+    ) -> Result<(), Status> {
         unimplemented!()
     }
 
-    fn log_static_fmt_val_static_str(&self, _fmt: &'static str, _v: RawVal, _s: &'static str) {
+    fn log_static_fmt_val_static_str(
+        &self,
+        _fmt: &'static str,
+        _v: RawVal,
+        _s: &'static str,
+    ) -> Result<(), Status> {
         unimplemented!()
     }
 
-    fn log_static_fmt_general(&self, _fmt: &'static str, _vals: &[RawVal], _strs: &[&'static str]) {
+    fn log_static_fmt_general(
+        &self,
+        _fmt: &'static str,
+        _vals: &[RawVal],
+        _strs: &[&'static str],
+    ) -> Result<(), Status> {
         unimplemented!()
     }
 }
```

### soroban-env-guest/src/guest.rs
```diff
@@ -32,31 +32,46 @@ impl EnvBase for Guest {
         unimplemented!()
     }
 
-    fn bytes_copy_from_slice(&self, b: Object, b_pos: RawVal, mem: &[u8]) -> Object {
+    fn bytes_copy_from_slice(
+        &self,
+        b: Object,
+        b_pos: RawVal,
+        mem: &[u8],
+    ) -> Result<Object, Status> {
         unimplemented!()
     }
 
-    fn bytes_copy_to_slice(&self, b: Object, b_pos: RawVal, mem: &mut [u8]) {
+    fn bytes_copy_to_slice(&self, b: Object, b_pos: RawVal, mem: &mut [u8]) -> Result<(), Status> {
         unimplemented!()
     }
 
-    fn bytes_new_from_slice(&self, mem: &[u8]) -> Object {
+    fn bytes_new_from_slice(&self, mem: &[u8]) -> Result<Object, Status> {
         unimplemented!()
     }
 
-    fn log_static_fmt_val(&self, fmt: &'static str, v: RawVal) {
+    fn log_static_fmt_val(&self, fmt: &'static str, v: RawVal) -> Result<(), Status> {
         unimplemented!()
     }
 
-    fn log_static_fmt_static_str(&self, fmt: &'static str, s: &'static str) {
+    fn log_static_fmt_static_str(&self, fmt: &'static str, s: &'static str) -> Result<(), Status> {
         unimplemented!()
     }
 
-    fn log_static_fmt_val_static_str(&self, fmt: &'static str, v: RawVal, s: &'static str) {
+    fn log_static_fmt_val_static_str(
+        &self,
+        fmt: &'static str,
+        v: RawVal,
+        s: &'static str,
+    ) -> Result<(), Status> {
         unimplemented!()
     }
 
-    fn log_static_fmt_general(&self, fmt: &'static str, vals: &[RawVal], strs: &[&'static str]) {
+    fn log_static_fmt_general(
+        &self,
+        fmt: &'static str,
+        vals: &[RawVal],
+        strs: &[&'static str],
+    ) -> Result<(), Status> {
         unimplemented!()
     }
 }
@@ -75,31 +90,39 @@ impl EnvBase for Guest {
         Self
     }
 
-    fn bytes_copy_from_slice(&self, b: Object, b_pos: RawVal, mem: &[u8]) -> Object {
+    fn bytes_copy_from_slice(
+        &self,
+        b: Object,
+        b_pos: RawVal,
+        mem: &[u8],
+    ) -> Result<Object, Status> {
         sa::assert_eq_size!(u32, *const u8);
         sa::assert_eq_size!(u32, usize);
         let lm_pos: RawVal = RawVal::from_u32(mem.as_ptr() as u32);
         let len: RawVal = RawVal::from_u32(mem.len() as u32);
-        self.bytes_copy_from_linear_memory(b, b_pos, lm_pos, len)
+        // NB: any failure in the host function here will trap the guest,
+        // not return, so we only have to code the happy path.
+        Ok(self.bytes_copy_from_linear_memory(b, b_pos, lm_pos, len))
     }
 
-    fn bytes_copy_to_slice(&self, b: Object, b_pos: RawVal, mem: &mut [u8]) {
+    fn bytes_copy_to_slice(&self, b: Object, b_pos: RawVal, mem: &mut [u8]) -> Result<(), Status> {
         sa::assert_eq_size!(u32, *const u8);
         sa::assert_eq_size!(u32, usize);
         let lm_pos: RawVal = RawVal::from_u32(mem.as_ptr() as u32);
         let len: RawVal = RawVal::from_u32(mem.len() as u32);
         self.bytes_copy_to_linear_memory(b, b_pos, lm_pos, len);
+        Ok(())
     }
 
-    fn bytes_new_from_slice(&self, mem: &[u8]) -> Object {
+    fn bytes_new_from_slice(&self, mem: &[u8]) -> Result<Object, Status> {
         sa::assert_eq_size!(u32, *const u8);
         sa::assert_eq_size!(u32, usize);
         let lm_pos: RawVal = RawVal::from_u32(mem.as_ptr() as u32);
         let len: RawVal = RawVal::from_u32(mem.len() as u32);
-        self.bytes_new_from_linear_memory(lm_pos, len)
+        Ok(self.bytes_new_from_linear_memory(lm_pos, len))
     }
 
-    fn log_static_fmt_val(&self, fmt: &'static str, v: RawVal) {
+    fn log_static_fmt_val(&self, fmt: &'static str, v: RawVal) -> Result<(), Status> {
         // TODO: It's possible we might want to do something in the wasm
         // case with static strings similar to the bytes functions above,
         // eg. decay the strings to u32 values and pass them to the host as linear
@@ -111,18 +134,32 @@ impl EnvBase for Guest {
         // it makes the debug buffer into non-Send+Sync and then we need
         // to remove it from the HostError, report separately from HostError's
         // Debug impl)
+        Ok(())
     }
 
-    fn log_static_fmt_static_str(&self, fmt: &'static str, s: &'static str) {
+    fn log_static_fmt_static_str(&self, fmt: &'static str, s: &'static str) -> Result<(), Status> {
         // Intentionally a no-op in this cfg. See above.
+        Ok(())
     }
 
-    fn log_static_fmt_val_static_str(&self, fmt: &'static str, v: RawVal, s: &'static str) {
+    fn log_static_fmt_val_static_str(
+        &self,
+        fmt: &'static str,
+        v: RawVal,
+        s: &'static str,
+    ) -> Result<(), Status> {
         // Intentionally a no-op in this cfg. See above.
+        Ok(())
     }
 
-    fn log_static_fmt_general(&self, fmt: &'static str, vals: &[RawVal], strs: &[&'static str]) {
+    fn log_static_fmt_general(
+        &self,
+        fmt: &'static str,
+        vals: &[RawVal],
+        strs: &[&'static str],
+    ) -> Result<(), Status> {
         // Intentionally a no-op in this cfg. See above.
+        Ok(())
     }
 }
 
```

### soroban-env-host/src/host.rs
```diff
@@ -975,80 +975,92 @@ impl EnvBase for Host {
         new_host
     }
 
-    fn bytes_copy_from_slice(&self, b: Object, b_pos: RawVal, mem: &[u8]) -> Object {
+    fn bytes_copy_from_slice(
+        &self,
+        b: Object,
+        b_pos: RawVal,
+        mem: &[u8],
+    ) -> Result<Object, Status> {
         // This is only called from native contracts, either when testing or
         // when the contract is otherwise linked into the same address space as
         // us. We therefore access the memory we were passed directly.
-        //
-        // This is also why we _panic_ on errors in here, rather than attempting
-        // to return a recoverable error code: native contracts that call this
-        // function do so through APIs that _should_ never pass bad data.
-        //
-        // TODO: we may revisit this choice of panicing in the future, depending
-        // on how we choose to try to contain panics-caused-by-native-contracts.
-        let b_pos = u32::try_from(b_pos).expect("pos input is not u32");
-        let len = u32::try_from(mem.len()).expect("slice len exceeds u32");
+        let b_pos = u32::try_from(b_pos).map_err(|_| ScHostValErrorCode::UnexpectedValType)?;
+        let len = u32::try_from(mem.len()).map_err(|_| ScHostValErrorCode::U32OutOfRange)?;
         let mut vnew = self
             .visit_obj(b, |hv: &Vec<u8>| Ok(hv.clone()))
-            .expect("access to unknown host bytes object");
-        let end_idx = b_pos.checked_add(len).expect("u32 overflow") as usize;
+            .map_err(|he| he.status)?;
+        let end_idx = b_pos
+            .checked_add(len)
+            .ok_or(ScHostValErrorCode::U32OutOfRange)? as usize;
         // TODO: we currently grow the destination vec if it's not big enough,
         // make sure this is desirable behaviour.
         if end_idx > vnew.len() {
             vnew.resize(end_idx, 0);
         }
+        self.validate_index_lt_bound(b_pos, vnew.len())
+            .map_err(|he| he.status)?;
         let write_slice = &mut vnew[b_pos as usize..end_idx];
         write_slice.copy_from_slice(mem);
         self.add_host_object(vnew)
-            .expect("unable to add host object")
-            .into()
+            .map(|ev| ev.into())
+            .map_err(|he| he.status)
     }
 
-    fn bytes_copy_to_slice(&self, b: Object, b_pos: RawVal, mem: &mut [u8]) {
-        let b_pos = u32::try_from(b_pos).expect("pos input is not u32");
-        let len = u32::try_from(mem.len()).expect("slice len exceeds u32");
+    fn bytes_copy_to_slice(&self, b: Object, b_pos: RawVal, mem: &mut [u8]) -> Result<(), Status> {
+        let b_pos = u32::try_from(b_pos).map_err(|_| ScHostValErrorCode::UnexpectedValType)?;
+        let len = u32::try_from(mem.len()).map_err(|_| ScHostValErrorCode::U32OutOfRange)?;
         self.visit_obj(b, move |hv: &Vec<u8>| {
-            let end_idx = b_pos.checked_add(len).expect("u32 overflow") as usize;
-            if end_idx > hv.len() {
-                panic!("index out of bounds");
-            }
-            mem.copy_from_slice(&hv.as_slice()[b_pos as usize..end_idx]);
+            let end_idx = b_pos
+                .checked_add(len)
+                .ok_or(ScHostValErrorCode::U32OutOfRange)?;
+            self.validate_index_lt_bound(b_pos, mem.len())?;
+            self.validate_index_le_bound(end_idx, mem.len())?;
+            mem.copy_from_slice(&hv.as_slice()[b_pos as usize..end_idx as usize]);
             Ok(())
         })
-        .expect("access to unknown host object");
+        .map_err(|he| he.status)
     }
 
-    fn bytes_new_from_slice(&self, mem: &[u8]) -> Object {
+    fn bytes_new_from_slice(&self, mem: &[u8]) -> Result<Object, Status> {
         self.add_host_object::<Vec<u8>>(mem.into())
-            .expect("unable to add host bytes object")
-            .into()
+            .map(|ev| ev.val)
+            .map_err(|he| he.status)
     }
 
-    fn log_static_fmt_val(&self, fmt: &'static str, v: RawVal) {
+    fn log_static_fmt_val(&self, fmt: &'static str, v: RawVal) -> Result<(), Status> {
         self.record_debug_event(DebugEvent::new().msg(fmt).arg(v))
-            .expect("unable to record debug event")
+            .map_err(|he| he.status)
     }
 
-    fn log_static_fmt_static_str(&self, fmt: &'static str, s: &'static str) {
+    fn log_static_fmt_static_str(&self, fmt: &'static str, s: &'static str) -> Result<(), Status> {
         self.record_debug_event(DebugEvent::new().msg(fmt).arg(s))
-            .expect("unable to record debug event")
+            .map_err(|he| he.status)
     }
 
-    fn log_static_fmt_val_static_str(&self, fmt: &'static str, v: RawVal, s: &'static str) {
+    fn log_static_fmt_val_static_str(
+        &self,
+        fmt: &'static str,
+        v: RawVal,
+        s: &'static str,
+    ) -> Result<(), Status> {
         self.record_debug_event(DebugEvent::new().msg(fmt).arg(v).arg(s))
-            .expect("unable to record debug event")
+            .map_err(|he| he.status)
     }
 
-    fn log_static_fmt_general(&self, fmt: &'static str, vals: &[RawVal], strs: &[&'static str]) {
+    fn log_static_fmt_general(
+        &self,
+        fmt: &'static str,
+        vals: &[RawVal],
+        strs: &[&'static str],
+    ) -> Result<(), Status> {
         let mut evt = DebugEvent::new().msg(fmt);
         for v in vals {
             evt = evt.arg(*v)
         }
         for s in strs {
             evt = evt.arg(*s)
         }
-        self.record_debug_event(evt)
-            .expect("unable to record debug event")
+        self.record_debug_event(evt).map_err(|he| he.status)
     }
 }
 
```

### soroban-env-host/src/native_contract/token/error.rs
```diff
@@ -1,12 +1,18 @@
 use crate::host::HostError;
-use soroban_env_common::ConversionError;
+use soroban_env_common::{ConversionError, Status};
 
 #[derive(Debug)]
 pub enum Error {
     HostError(HostError),
     ContractError,
 }
 
+impl From<Status> for Error {
+    fn from(s: Status) -> Self {
+        Error::HostError(s.into())
+    }
+}
+
 impl From<ConversionError> for Error {
     fn from(e: ConversionError) -> Self {
         Error::HostError(e.into())
```

### soroban-env-host/src/native_contract/token/metadata.rs
```diff
@@ -20,7 +20,7 @@ pub fn read_metadata(e: &Host) -> Result<Metadata, Error> {
 pub fn read_name(e: &Host) -> Result<Bytes, Error> {
     match read_metadata(e)? {
         Metadata::Token(token) => Ok(token.name),
-        Metadata::Native => Ok(Bytes::try_from_val(e, e.bytes_new_from_slice(b"native"))?),
+        Metadata::Native => Ok(Bytes::try_from_val(e, e.bytes_new_from_slice(b"native")?)?),
         Metadata::AlphaNum4(asset) => {
             let mut res: Bytes = asset.asset_code.into();
             res.push(b':')?;
@@ -39,7 +39,7 @@ pub fn read_name(e: &Host) -> Result<Bytes, Error> {
 pub fn read_symbol(e: &Host) -> Result<Bytes, Error> {
     match read_metadata(e)? {
         Metadata::Token(token) => Ok(token.symbol),
-        Metadata::Native => Ok(Bytes::try_from_val(e, e.bytes_new_from_slice(b"native"))?),
+        Metadata::Native => Ok(Bytes::try_from_val(e, e.bytes_new_from_slice(b"native")?)?),
         Metadata::AlphaNum4(asset) => Ok(asset.asset_code.into()),
         Metadata::AlphaNum12(asset) => Ok(asset.asset_code.into()),
     }
```

### soroban-env-host/src/test/account.rs
```diff
@@ -35,9 +35,9 @@ fn check_account_exists() -> Result<(), HostError> {
     );
 
     let host = Host::with_storage_and_budget(storage, budget.clone());
-    let obj0 = host.bytes_new_from_slice(&id0);
-    let obj1 = host.bytes_new_from_slice(&id1);
-    let obj2 = host.bytes_new_from_slice(&id2);
+    let obj0 = host.bytes_new_from_slice(&id0)?;
+    let obj1 = host.bytes_new_from_slice(&id1)?;
+    let obj2 = host.bytes_new_from_slice(&id2)?;
     // declared and exists
     assert_eq!(
         host.account_exists(obj0)?.get_payload(),
```

### soroban-env-host/src/test/bytes.rs
```diff
@@ -99,7 +99,7 @@ fn bytes_put_out_of_bound() -> Result<(), HostError> {
 #[test]
 fn bytes_slice_start_greater_than_end() -> Result<(), HostError> {
     let host = Host::default();
-    let obj = host.bytes_new_from_slice(&[1, 2, 3, 4]);
+    let obj = host.bytes_new_from_slice(&[1, 2, 3, 4])?;
     let res = host.bytes_slice(obj, 2_u32.into(), 1_u32.into());
     let code = ScHostFnErrorCode::InputArgsInvalid;
     assert!(HostError::result_matches_err_status(res, code));
@@ -109,7 +109,7 @@ fn bytes_slice_start_greater_than_end() -> Result<(), HostError> {
 #[test]
 fn bytes_slice_start_equal_len() -> Result<(), HostError> {
     let host = Host::default();
-    let obj = host.bytes_new_from_slice(&[1, 2, 3, 4]);
+    let obj = host.bytes_new_from_slice(&[1, 2, 3, 4])?;
     let res = host.bytes_slice(obj, 4_u32.into(), 4_u32.into())?;
     assert_eq!(host.obj_cmp(res.into(), host.bytes_new()?.into())?, 0);
     Ok(())
@@ -118,7 +118,7 @@ fn bytes_slice_start_equal_len() -> Result<(), HostError> {
 #[test]
 fn bytes_slice_start_greater_than_len() -> Result<(), HostError> {
     let host = Host::default();
-    let obj = host.bytes_new_from_slice(&[1, 2, 3, 4]);
+    let obj = host.bytes_new_from_slice(&[1, 2, 3, 4])?;
     let res = host.bytes_slice(obj, 5_u32.into(), 10_u32.into());
     let code = ScHostObjErrorCode::VecIndexOutOfBound;
     assert!(HostError::result_matches_err_status(res, code));
```
