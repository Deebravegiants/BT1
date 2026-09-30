# [?] fix: deadlock.

## Summary
Severity: Unknown
Chain: Movement
Component: movement-network/movement
Published: 2024-06-24
Source: https://github.com/movement-network/movement/commit/940a8fb452a606a3dca5f177db4178a758b11419
Type: security-commit

## Details
fix: deadlock.

## Patch
### util/flocks/src/frwlock/mod.rs
```diff
@@ -19,46 +19,47 @@ pub enum FrwLockError {
     FileError(#[from] std::io::Error),
 }
 
+/// A file-based read-write lock.
+/// This only mutually excludes processes trying to violate the lock, not the same process--which is not considered contention.
+/// If you want to prevent contention within the same process, you should wrap this in your preferred synchronization primitive.
 pub struct FrwLock<T: AsFd> {
-    cell: UnsafeCell<T>,
+    cell: UnsafeCell<T>
 }
 
 impl<T: AsFd> FrwLock<T> {
     pub fn new(file: T) -> Self {
         Self {
-            cell: UnsafeCell::new(file),
+            cell: UnsafeCell::new(file)
         }
     }
 
-    pub(crate) fn try_write(&self) -> Result<FrwLockWriteGuard<'_, T>, FrwLockError> {
+    pub(crate) fn try_write(&self) -> Result<FrwLockWriteGuard<T>, FrwLockError> {
         let file = unsafe { &*self.cell.get() };
         match flock(file, FlockOperation::NonBlockingLockExclusive) {
             Ok(_) => {
                 Ok(FrwLockWriteGuard {
                     data: self.cell.get(),
-                    _marker: std::marker::PhantomData,
                 })
             },
             Err(rustix::io::Errno::WOULDBLOCK) => Err(FrwLockError::LockNotAvailable),
             Err(e) => Err(FrwLockError::FileError(e.into())),
         }
     }
 
-    pub(crate) fn try_read(&self) -> Result<FrwLockReadGuard<'_, T>, FrwLockError> {
+    pub(crate) fn try_read(&self) -> Result<FrwLockReadGuard<T>, FrwLockError> {
         let file = unsafe { &*self.cell.get() };
         match flock(file, FlockOperation::NonBlockingLockShared) {
             Ok(_) => {
                 Ok(FrwLockReadGuard {
                     data: self.cell.get(),
-                    _marker: std::marker::PhantomData,
                 })
             },
             Err(rustix::io::Errno::WOULDBLOCK) => Err(FrwLockError::LockNotAvailable),
             Err(e) => Err(FrwLockError::FileError(e.into())),
         }
     }
 
-    pub async fn write(&self) -> Result<FrwLockWriteGuard<'_, T>, FrwLockError> {
+    pub async fn write(&self) -> Result<FrwLockWriteGuard<T>, FrwLockError> {
         loop {
             match self.try_write() {
                 Ok(guard) => return Ok(guard),
@@ -71,7 +72,7 @@ impl<T: AsFd> FrwLock<T> {
         }
     }
 
-    pub async fn read(&self) -> Result<FrwLockReadGuard<'_, T>, FrwLockError> {
+    pub async fn read(&self) -> Result<FrwLockReadGuard<T>, FrwLockError> {
         loop {
             match self.try_read() {
                 Ok(guard) => return Ok(guard),
@@ -93,10 +94,10 @@ unsafe impl<T> Sync for FrwLock<T> where T: AsFd + Sized + Send + Sync {}
 // NB: These impls need to be explicit since we're storing a raw pointer.
 // Safety: Stores a raw pointer to `T`, so if `T` is `Sync`, the lock guard over
 // `T` is `Send`.
-unsafe impl<T> Send for FrwLockReadGuard<'_, T> where T: AsFd + Sized + Sync {}
-unsafe impl<T> Sync for FrwLockReadGuard<'_, T> where T: AsFd + Sized + Send + Sync {}
-unsafe impl<T> Send for FrwLockWriteGuard<'_, T> where T: AsFd + Sized + Sync {}
-unsafe impl<T> Sync for FrwLockWriteGuard<'_, T> where T: AsFd + Sized + Send + Sync {}
+unsafe impl<T> Send for FrwLockReadGuard<T> where T: AsFd + Sized + Sync {}
+unsafe impl<T> Sync for FrwLockReadGuard<T> where T: AsFd + Sized + Send + Sync {}
+unsafe impl<T> Send for FrwLockWriteGuard<T> where T: AsFd + Sized + Sync {}
+unsafe impl<T> Sync for FrwLockWriteGuard<T> where T: AsFd + Sized + Send + Sync {}
 
 #[cfg(test)]
 mod tests {
```

### util/flocks/src/frwlock/read_guard.rs
```diff
@@ -1,28 +1,25 @@
-use std::marker::PhantomData;
 use std::ops::Deref;
 use rustix::{
     fs::{flock, FlockOperation},
-    fd::AsFd,
+    fd::AsFd
 };
 
-pub struct FrwLockReadGuard<'a, T: AsFd> {
-    pub(crate) data: *const T,
-    pub(crate) _marker: PhantomData<&'a T>, // Ensuring lifetime and immutability semantics.
+pub struct FrwLockReadGuard<T: AsFd> {
+    pub(crate) data: *const T
 }
 
-impl<T: AsFd> Deref for FrwLockReadGuard<'_, T> {
+impl<T: AsFd> Deref for FrwLockReadGuard<T> {
     type Target = T;
 
     fn deref(&self) -> &Self::Target {
         unsafe { &*self.data }
     }
 }
 
-impl<T: AsFd> Drop for FrwLockReadGuard<'_, T> {
+impl<T: AsFd> Drop for FrwLockReadGuard<T> {
     fn drop(&mut self) {
         flock(
-            unsafe { &*self.data },
-            FlockOperation::Unlock,
-        ).expect("Failed to unlock file");
+            unsafe { &*self.data }, 
+            FlockOperation::Unlock).expect("Failed to unlock file");
     }
-}
+}
\ No newline at end of file
```

### util/flocks/src/frwlock/write_guard.rs
```diff
@@ -1,34 +1,31 @@
-use std::marker::PhantomData;
 use std::ops::{Deref, DerefMut};
 use rustix::{
     fs::{flock, FlockOperation},
-    fd::AsFd,
+    fd::AsFd
 };
 
-pub struct FrwLockWriteGuard<'a, T: AsFd> {
-    pub(crate) data: *mut T,
-    pub(crate) _marker: PhantomData<&'a mut T>, // Ensuring lifetime and mutability semantics.
+pub struct FrwLockWriteGuard<T: AsFd> {
+    pub(crate) data: *mut T
 }
 
-impl<T: AsFd> Deref for FrwLockWriteGuard<'_, T> {
+impl<T: AsFd> Deref for FrwLockWriteGuard<T> {
     type Target = T;
 
     fn deref(&self) -> &Self::Target {
         unsafe { &*self.data }
     }
 }
 
-impl<T: AsFd> DerefMut for FrwLockWriteGuard<'_, T> {
+impl<T: AsFd> DerefMut for FrwLockWriteGuard<T> {
     fn deref_mut(&mut self) -> &mut Self::Target {
         unsafe { &mut *self.data }
     }
 }
 
-impl<T: AsFd> Drop for FrwLockWriteGuard<'_, T> {
+impl <T: AsFd> Drop for FrwLockWriteGuard<T> {
     fn drop(&mut self) {
         flock(
             unsafe { &*self.data },
-            FlockOperation::Unlock,
-        ).expect("Failed to unlock file");
+    FlockOperation::Unlock).expect("Failed to unlock file");
     }
 }
\ No newline at end of file
```

### util/flocks/src/tfrwlock/mod.rs
```diff
@@ -1,13 +1,14 @@
-pub mod read_guard;
 pub mod write_guard;
+pub mod read_guard;
 
 pub use write_guard::TfrwLockWriteGuard;
 pub use read_guard::TfrwLockReadGuard;
 
 use tokio::sync::RwLock;
+use crate::frwlock::{FrwLock, FrwLockError};
 use rustix::fd::AsFd;
 use thiserror::Error;
-use crate::frwlock::{FrwLock, FrwLockError};
+
 
 #[derive(Debug, Error)]
 pub enum TfrwLockError {
@@ -26,24 +27,29 @@ impl From<FrwLockError> for TfrwLockError {
     }
 }
 
+/// A file-based read-write lock.
+/// This only mutually excludes processes trying to violate the lock, not the same process--which is not considered contention.
+/// If you want to prevent contention within the same process, you should wrap this in your preferred synchronization primitive.
 pub struct TfrwLock<T: AsFd> {
-    lock: RwLock<FrwLock<T>>,
+    lock : RwLock<FrwLock<T>>
 }
 
 impl<T: AsFd> TfrwLock<T> {
     pub fn new(file: T) -> Self {
         Self {
-            lock: RwLock::new(FrwLock::new(file)),
+            lock: RwLock::new(FrwLock::new(file))
         }
     }
 
-    pub async fn write<'a>(&'a self) -> Result<TfrwLockWriteGuard<'a, T>, TfrwLockError> {
+    pub async fn write(&self) -> Result<TfrwLockWriteGuard<T>, TfrwLockError> {
         let outer_guard = self.lock.write().await;
-        TfrwLockWriteGuard::new(outer_guard).map_err(|e| e.into())
+        let inner_guard = outer_guard.write().await?;
+        Ok(TfrwLockWriteGuard::new(outer_guard, inner_guard))
     }
 
-    pub async fn read<'a>(&'a self) -> Result<TfrwLockReadGuard<'a, T>, TfrwLockError> {
+    pub async fn read(&self) -> Result<TfrwLockReadGuard<T>, TfrwLockError> {
         let outer_guard = self.lock.read().await;
-        TfrwLockReadGuard::new(outer_guard).map_err(|e| e.into())
+        let inner_guard = outer_guard.read().await?;
+        Ok(TfrwLockReadGuard::new(outer_guard, inner_guard))
     }
 }
\ No newline at end of file
```

### util/flocks/src/tfrwlock/read_guard.rs
```diff
@@ -1,30 +1,23 @@
 use std::ops::Deref;
 use tokio::sync::RwLockReadGuard;
 use rustix::fd::AsFd;
-use crate::frwlock::{FrwLock, FrwLockReadGuard, FrwLockError};
+use crate::frwlock::{FrwLock, FrwLockReadGuard};
 
 pub struct TfrwLockReadGuard<'a, T: AsFd> {
     _outer: RwLockReadGuard<'a, FrwLock<T>>,
-    inner: Option<FrwLockReadGuard<'a, T>>,
+    inner: FrwLockReadGuard<T>,
 }
 
 impl<'a, T: AsFd> TfrwLockReadGuard<'a, T> {
-    pub(crate) fn new(mut outer: RwLockReadGuard<'a, FrwLock<T>>) -> Result<Self, FrwLockError> {
-        let inner = outer.try_read().ok().map(|inner_guard| Self {
-            _outer: outer,
-            inner: Some(inner_guard),
-        });
-        match inner {
-            Some(guard) => Ok(guard),
-            None => Err(FrwLockError::LockNotAvailable),
-        }
+    pub(crate) fn new(outer: RwLockReadGuard<'a, FrwLock<T>>, inner: FrwLockReadGuard<T>) -> Self {
+        Self { _outer : outer, inner }
     }
 }
 
 impl<'a, T: AsFd> Deref for TfrwLockReadGuard<'a, T> {
     type Target = T;
 
     fn deref(&self) -> &Self::Target {
-        &*self.inner.as_ref().unwrap()
+        &*self.inner
     }
 }
\ No newline at end of file
```

### util/flocks/src/tfrwlock/write_guard.rs
```diff
@@ -1,37 +1,29 @@
+use std::ops::{Deref, DerefMut};
 use tokio::sync::RwLockWriteGuard;
 use rustix::fd::AsFd;
-use crate::frwlock::{FrwLock, FrwLockWriteGuard, FrwLockError};
-use std::ops::{Deref, DerefMut};
-
+use crate::frwlock::{FrwLock, FrwLockWriteGuard};
 
 pub struct TfrwLockWriteGuard<'a, T: AsFd> {
     _outer: RwLockWriteGuard<'a, FrwLock<T>>,
-    inner: Option<FrwLockWriteGuard<'a, T>>,
+    inner: FrwLockWriteGuard<T>,
 }
 
 impl<'a, T: AsFd> TfrwLockWriteGuard<'a, T> {
-    pub(crate) fn new(mut outer: RwLockWriteGuard<'a, FrwLock<T>>) -> Result<Self, FrwLockError> {
-        let inner = outer.try_write().ok().map(|inner_guard| Self {
-            _outer: outer,
-            inner: Some(inner_guard),
-        });
-        match inner {
-            Some(guard) => Ok(guard),
-            None => Err(FrwLockError::LockNotAvailable),
-        }
+    pub(crate) fn new(outer: RwLockWriteGuard<'a, FrwLock<T>>, inner: FrwLockWriteGuard<T>) -> Self {
+        Self { _outer : outer, inner }
     }
 }
 
 impl<'a, T: AsFd> Deref for TfrwLockWriteGuard<'a, T> {
     type Target = T;
 
     fn deref(&self) -> &Self::Target {
-        &*self.inner.as_ref().unwrap()
+        &*self.inner
     }
 }
 
 impl<'a, T: AsFd> DerefMut for TfrwLockWriteGuard<'a, T> {
     fn deref_mut(&mut self) -> &mut Self::Target {
-        &mut *self.inner.as_mut().unwrap()
+        &mut *self.inner
     }
 }
\ No newline at end of file
```
