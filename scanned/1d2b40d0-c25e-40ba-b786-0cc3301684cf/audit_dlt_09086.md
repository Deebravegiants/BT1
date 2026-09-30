# [?] fix(core): Avoid out-of-bounds read in utils.consteq().

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2026-04-17
Source: https://github.com/trezor/trezor-firmware/commit/8f19041deb9ff267cd2dc3b5722a53e7982ab2ad
Type: security-commit

## Details
fix(core): Avoid out-of-bounds read in utils.consteq().

[no changelog]

## Patch
### core/embed/upymod/modtrezorutils/modtrezorutils.c
```diff
@@ -98,20 +98,23 @@ STATIC MP_DEFINE_CONST_FUN_OBJ_0(mod_trezorutils_telemetry_get_obj,
 /// def consteq(sec: AnyBytes, pub: AnyBytes) -> bool:
 ///     """
 ///     Compares the private information in `sec` with public, user-provided
-///     information in `pub`.  Runs in constant time, corresponding to a length
-///     of `pub`.  Can access memory behind valid length of `sec`, caller is
-///     expected to avoid any invalid memory access.
+///     information in `pub`.  Runs in constant time, corresponding to the
+///     length of `pub`.
 ///     """
 STATIC mp_obj_t mod_trezorutils_consteq(mp_obj_t sec, mp_obj_t pub) {
   mp_buffer_info_t secbuf = {0};
   mp_get_buffer_raise(sec, &secbuf, MP_BUFFER_READ);
   mp_buffer_info_t pubbuf = {0};
   mp_get_buffer_raise(pub, &pubbuf, MP_BUFFER_READ);
 
-  size_t diff = secbuf.len - pubbuf.len;
+  // Redirect s to p when lengths differ so the loop cannot read past sec,
+  // while keeping the instruction count independent of the secret length.
+  uint8_t diff = (secbuf.len != pubbuf.len);
+  uintptr_t mask = -(uintptr_t)diff;
+  const uint8_t *s = (const uint8_t *)(((uintptr_t)secbuf.buf & ~mask) |
+                                       ((uintptr_t)pubbuf.buf & mask));
+  const uint8_t *p = (const uint8_t *)pubbuf.buf;
   for (size_t i = 0; i < pubbuf.len; i++) {
-    const uint8_t *s = (uint8_t *)secbuf.buf;
-    const uint8_t *p = (uint8_t *)pubbuf.buf;
     diff |= s[i] - p[i];
   }
 
```

### core/mocks/generated/trezorutils.pyi
```diff
@@ -24,9 +24,8 @@ def telemetry_get() -> tuple[int, int, int, int] | None:
 def consteq(sec: AnyBytes, pub: AnyBytes) -> bool:
     """
     Compares the private information in `sec` with public, user-provided
-    information in `pub`.  Runs in constant time, corresponding to a length
-    of `pub`.  Can access memory behind valid length of `sec`, caller is
-    expected to avoid any invalid memory access.
+    information in `pub`.  Runs in constant time, corresponding to the
+    length of `pub`.
     """
 
 
```

### core/tests/test_trezor.utils.py
```diff
@@ -101,6 +101,22 @@ def test_memzero(self):
         utils.memzero(data)
         self.assertEqual(data, bytearray(10))
 
+    def test_consteq(self):
+        self.assertTrue(utils.consteq(b"", b""))
+        self.assertFalse(utils.consteq(b"", b"\x42"))
+        self.assertFalse(utils.consteq(b"\x42", b""))
+        self.assertFalse(utils.consteq(b"hell", b"hello"))
+        self.assertFalse(utils.consteq(b"hello", b"ello"))
+        long1 = b"x" * 999 + b"y"
+        long2 = b"x" * 1000
+        self.assertFalse(utils.consteq(bytearray(long1), long2))
+        self.assertFalse(utils.consteq(long1, bytearray(long2)))
+        self.assertTrue(utils.consteq(long1, bytearray(long1)))
+        self.assertTrue(utils.consteq(bytearray(long1), long1))
+        self.assertFalse(utils.consteq(b"", long1))
+        self.assertTrue(utils.consteq(memoryview(b"hello"), b"hello"))
+        self.assertTrue(utils.consteq(b"hello", memoryview(b"hello")))
+
 
 if __name__ == "__main__":
     unittest.main()
```
