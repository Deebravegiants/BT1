# [?] Merge #8373: Fix OSX non-deterministic dmg

## Summary
Severity: Unknown
Chain: Dogecoin
Component: dogecoin/dogecoin
Published: 2016-07-20
Source: https://github.com/dogecoin/dogecoin/commit/c98abf2c7099fa089cd9170dcdd118ba86356ffc
Type: security-commit

## Details
Merge #8373: Fix OSX non-deterministic dmg

3b3ce25 build: fix non-deterministic biplist (Cory Fields)

## Patch
### depends/packages/native_biplist.mk
```diff
@@ -4,6 +4,11 @@ $(package)_download_path=https://pypi.python.org/packages/source/b/biplist
 $(package)_file_name=biplist-$($(package)_version).tar.gz
 $(package)_sha256_hash=b57cadfd26e4754efdf89e9e37de87885f9b5c847b2615688ca04adfaf6ca604
 $(package)_install_libdir=$(build_prefix)/lib/python/dist-packages
+$(package)_patches=sorted_list.patch
+
+define $(package)_preprocess_cmds
+  patch -p1 < $($(package)_patch_dir)/sorted_list.patch
+endef
 
 define $(package)_build_cmds
     python setup.py build
```

### depends/patches/native_biplist/sorted_list.patch
```diff
@@ -0,0 +1,29 @@
+--- a/biplist/__init__.py	2014-10-26 19:03:11.000000000 +0000
++++ b/biplist/__init__.py	2016-07-19 19:30:17.663521999 +0000
+@@ -541,7 +541,7 @@
+             return HashableWrapper(n)
+         elif isinstance(root, dict):
+             n = {}
+-            for key, value in iteritems(root):
++            for key, value in sorted(iteritems(root)):
+                 n[self.wrapRoot(key)] = self.wrapRoot(value)
+             return HashableWrapper(n)
+         elif isinstance(root, list):
+@@ -616,7 +616,7 @@
+             elif isinstance(obj, dict):
+                 size = proc_size(len(obj))
+                 self.incrementByteCount('dictBytes', incr=1+size)
+-                for key, value in iteritems(obj):
++                for key, value in sorted(iteritems(obj)):
+                     check_key(key)
+                     self.computeOffsets(key, asReference=True)
+                     self.computeOffsets(value, asReference=True)
+@@ -714,7 +714,7 @@
+                 keys = []
+                 values = []
+                 objectsToWrite = []
+-                for key, value in iteritems(obj):
++                for key, value in sorted(iteritems(obj)):
+                     keys.append(key)
+                     values.append(value)
+                 for key in keys:
```
