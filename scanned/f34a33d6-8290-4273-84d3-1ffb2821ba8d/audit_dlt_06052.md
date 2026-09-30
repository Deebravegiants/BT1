# [?] Merge #20479: Fix QPainter non-determinism on macOS (0.21 backport)

## Summary
Severity: Unknown
Chain: Litecoin
Component: litecoin-project/litecoin
Published: 2020-11-25
Source: https://github.com/litecoin-project/litecoin/commit/17294c1820396791f436e659432c5d0a976c6554
Type: security-commit

## Details
Merge #20479: Fix QPainter non-determinism on macOS (0.21 backport)

ab23a83400d5ad13137ce0f9697a51f0b70e9d29 Fix QPainter non-determinism on macOS (Andrew Chow)

Pull request description:

  Aplies a patch to Qt that fixes the non-determinism by modifying Qt. The
  source of the non-determinism is how LLVM 8 optimizes qt_intersect_spans
  when compiling. The particular optimization that seems to be causing the
  problems is that a temp variable is being added for spans->y. For some
  reason, when it does this, it chooses different instructions to use when
  making that variable. We bypass this problem by patching
  qt_intersect_spans to always make and use this local variable.

  Github-Pull: #20447
  Rebased-From: 8f7d1b39efbe65ab2747c593cc3560d4a449a333
  Tree-SHA512: 558da5c2bb0373e2a89f2c219170f802036e0e87cc8e808336b23d074152cb893007a440f46ec957156b0921355cd18502710f2d224f27bc26e934c50ebebc41

ACKs for top commit:
  jonasschnelli:
    codereview ACK ab23a83400d5ad13137ce0f9697a51f0b70e9d29
  achow101:
    ACK ab23a83400d5ad13137ce0f9697a51f0b70e9d29

Tree-SHA512: 10991fe2b5452b1393678c315281cfdca011e9bb2cd8094a002746e690890ace148ac2dbf39c5fbe5e7f4cd39eeebfa0a715c065cff150cf70e9733cb0ff32d6

## Patch
### depends/packages/qt.mk
```diff
@@ -12,6 +12,7 @@ $(package)_patches=fix_qt_pkgconfig.patch mac-qmake.conf fix_configure_mac.patch
 $(package)_patches+= fix_rcc_determinism.patch fix_riscv64_arch.patch xkb-default.patch no-xlib.patch
 $(package)_patches+= fix_android_qmake_conf.patch fix_android_jni_static.patch dont_hardcode_pwd.patch
 $(package)_patches+= freetype_back_compat.patch drop_lrelease_dependency.patch fix_powerpc_libpng.patch
+$(package)_patches+= fix_qpainter_non_determinism.patch
 
 # Update OSX_QT_TRANSLATIONS when this is updated
 $(package)_qttranslations_file_name=qttranslations-$($(package)_suffix)
@@ -195,6 +196,7 @@ endef
 define $(package)_preprocess_cmds
   patch -p1 -i $($(package)_patch_dir)/freetype_back_compat.patch && \
   patch -p1 -i $($(package)_patch_dir)/fix_powerpc_libpng.patch && \
+  patch -p1 -i $($(package)_patch_dir)/fix_qpainter_non_determinism.patch &&\
   sed -i.old "s|updateqm.commands = \$$$$\$$$$LRELEASE|updateqm.commands = $($(package)_extract_dir)/qttools/bin/lrelease|" qttranslations/translations/translations.pro && \
   patch -p1 -i $($(package)_patch_dir)/drop_lrelease_dependency.patch && \
   patch -p1 -i $($(package)_patch_dir)/dont_hardcode_pwd.patch &&\
```

### depends/patches/qt/fix_qpainter_non_determinism.patch
```diff
@@ -0,0 +1,63 @@
+commit 2a8f7dc6ddfc414a66491522501c1574a1343ee1
+Author: Andrew Chow <achow101-github@achow101.com>
+Date:   Sat Nov 21 01:11:04 2020 -0500
+
+    build: Fix determinism issue when building with Clang 8
+
+    When building Qt with LLVM/Clang 8 under -O3 (the default), we run into
+    a determinism issue in `qt_interset_spans`. The issue has been fixed for
+    LLVM/Clang 9, see
+    https://github.com/llvm/llvm-project/commit/db101864bdc938deb1d63fe4f7da761bd38e5cae
+    and https://reviews.llvm.org/D64601, however this fix was not backported
+    to 8.x. Once LLVM/Clang 9 is used, this patch can be dropped.
+
+    The particular issue appears to be an optimization done by -O3 which
+    adds a temporary variable for `spans->y` in `qt_intersect_spans`. When
+    it does this, sometimes it chooses to use a 32-bit movs instruction
+    (movswl), and other times it chooses a 64-bit movs instruction (movswq).
+    By patching `qt_intersect_spans` to always make a temporary variable for
+    `spans->y`, we are able to sidestep this problem.
+
+diff --git a/qtbase/src/gui/painting/qpaintengine_raster.cpp b/qtbase/src/gui/painting/qpaintengine_raster.cpp
+index 92ab6e8375..f018009e0b 100644
+--- a/qtbase/src/gui/painting/qpaintengine_raster.cpp
++++ b/qtbase/src/gui/painting/qpaintengine_raster.cpp
+@@ -3971,22 +3971,23 @@ static const QSpan *qt_intersect_spans(const QClipData *clip, int *currentClip,
+     const QSpan *clipEnd = clip->m_spans + clip->count;
+ 
+     while (available && spans < end ) {
++        const short spans_y = spans->y;
+         if (clipSpans >= clipEnd) {
+             spans = end;
+             break;
+         }
+-        if (clipSpans->y > spans->y) {
++        if (clipSpans->y > spans_y) {
+             ++spans;
+             continue;
+         }
+-        if (spans->y != clipSpans->y) {
+-            if (spans->y < clip->count && clip->m_clipLines[spans->y].spans)
+-                clipSpans = clip->m_clipLines[spans->y].spans;
++        if (spans_y != clipSpans->y) {
++            if (spans_y < clip->count && clip->m_clipLines[spans_y].spans)
++                clipSpans = clip->m_clipLines[spans_y].spans;
+             else
+                 ++clipSpans;
+             continue;
+         }
+-        Q_ASSERT(spans->y == clipSpans->y);
++        Q_ASSERT(spans_y == clipSpans->y);
+ 
+         int sx1 = spans->x;
+         int sx2 = sx1 + spans->len;
+@@ -4005,7 +4006,7 @@ static const QSpan *qt_intersect_spans(const QClipData *clip, int *currentClip,
+         if (len) {
+             out->x = qMax(sx1, cx1);
+             out->len = qMin(sx2, cx2) - out->x;
+-            out->y = spans->y;
++            out->y = spans_y;
+             out->coverage = qt_div_255(spans->coverage * clipSpans->coverage);
+             ++out;
+             --available;
+
```
