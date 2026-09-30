# [?] "Fix" non-determinism in native_cctools build

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2019-11-18
Source: https://github.com/monero-project/monero/commit/abeed9a767ae68389fb1fae9f0bd4affc886e610
Type: security-commit

## Details
"Fix" non-determinism in native_cctools build

By omitting the otool binary which is built non-deterministically.
We don't use it anyway.

## Patch
### contrib/depends/packages/native_cctools.mk
```diff
@@ -10,6 +10,7 @@ $(package)_clang_download_file=clang+llvm-$($(package)_clang_version)-x86_64-lin
 $(package)_clang_file_name=clang-llvm-$($(package)_clang_version)-x86_64-linux-gnu-ubuntu-14.04.tar.xz
 $(package)_clang_sha256_hash=99b28a6b48e793705228a390471991386daa33a9717cd9ca007fcdde69608fd9
 $(package)_extra_sources=$($(package)_clang_file_name)
+$(package)_patches=skip_otool.patch
 
 define $(package)_fetch_cmds
 $(call fetch_file,$(package),$($(package)_download_path),$($(package)_download_file),$($(package)_file_name),$($(package)_sha256_hash)) && \
@@ -37,7 +38,10 @@ $(package)_cc=$($(package)_extract_dir)/toolchain/bin/clang
 $(package)_cxx=$($(package)_extract_dir)/toolchain/bin/clang++
 endef
 
+# If clang gets updated to a version with a fix for https://reviews.llvm.org/D50559
+# then the patch that skips otool can be removed.
 define $(package)_preprocess_cmds
+  patch -p0 < $($(package)_patch_dir)/skip_otool.patch && \
   cd $($(package)_build_subdir); ./autogen.sh && \
   sed -i.old "/define HAVE_PTHREADS/d" ld64/src/ld/InputFiles.h
 endef
```

### contrib/depends/patches/native_cctools/skip_otool.patch
```diff
@@ -0,0 +1,12 @@
+--- cctools/Makefile.am.O	2016-06-09 15:06:16.000000000 +0100
++++ cctools/Makefile.am	2019-11-18 08:59:20.078663220 +0000
+@@ -1,7 +1,7 @@
+ if ISDARWIN
+-SUBDIRS=libstuff ar as misc otool ld64 $(LD_CLASSIC)
++SUBDIRS=libstuff ar as misc ld64 $(LD_CLASSIC)
+ else
+-SUBDIRS=libstuff ar as misc libobjc2 otool ld64 $(LD_CLASSIC)
++SUBDIRS=libstuff ar as misc ld64 $(LD_CLASSIC)
+ endif
+ 
+ ACLOCAL_AMFLAGS = -I m4
```
