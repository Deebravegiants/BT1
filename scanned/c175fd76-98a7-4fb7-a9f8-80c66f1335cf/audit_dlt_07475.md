# [?] fix: follow-up #6596 disable -Wno-stringop-overread and -Wno-stringop-overflow

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2025-04-01
Source: https://github.com/dashpay/dash/commit/1e062a6654d4e74073e3b7d53af8d7fa24e134b1
Type: security-commit

## Details
fix: follow-up #6596 disable -Wno-stringop-overread and -Wno-stringop-overflow

When compiling with -O3 and gcc 14 I got these compilation errors (multiple places):

    In file included from /usr/include/c++/14/algorithm:60,
                     from ./test/fuzz/FuzzedDataProvider.h:16,
                     from test/fuzz/crypto_common.cpp:6:
    In function ‘constexpr typename __gnu_cxx::__enable_if<std::__is_byte<_Tp>::__value, void>::__type std::__fill_a1(_Tp*, _Tp*, const _Tp&) [with _Tp = unsigned char]’,
        inlined from ‘constexpr void std::__fill_a(_FIte, _FIte, const _Tp&) [with _FIte = unsigned char*; _Tp = unsigned char]’ at /usr/include/c++/14/bits/stl_algobase.h:998:21,
        inlined from ‘constexpr _OutputIterator std::__fill_n_a(_OutputIterator, _Size, const _Tp&, random_access_iterator_tag) [with _OutputIterator = unsigned char*; _Size = long unsigned int; _Tp = unsigned char]’ at /usr/include/c++/14/bits/stl_algobase.h:1151:20,
        inlined from ‘constexpr _OI std::fill_n(_OI, _Size, const _Tp&) [with _OI = unsigned char*; _Size = long unsigned int; _Tp = unsigned char]’ at /usr/include/c++/14/bits/stl_algobase.h:1180:29,
        inlined from ‘static constexpr _ForwardIterator std::__uninitialized_default_n_1<true>::__uninit_default_n(_ForwardIterator, _Size) [with _ForwardIterator = unsigned char*; _Size = long unsigned int]’ at /usr/include/c++/14/bits/stl_uninitialized.h:668:29,
        inlined from ‘static constexpr _ForwardIterator std::__uninitialized_default_n_1<true>::__uninit_default_n(_ForwardIterator, _Size) [with _ForwardIterator = unsigned char*; _Size = long unsigned int]’ at /usr/include/c++/14/bits/stl_uninitialized.h:660:9,
        inlined from ‘constexpr _ForwardIterator std::__uninitialized_default_n(_ForwardIterator, _Size) [with _ForwardIterator = unsigned char*; _Size = long unsigned int]’ at /usr/include/c++/14/bits/stl_uninitialized.h:712:20,
        inlined from ‘constexpr _ForwardIterator std::__uninitialized_default_n_a(_ForwardIterator, _Size, allocator<_Tp>&) [with _ForwardIterator = unsigned char*; _Size = long unsigned int; _Tp = unsigned char]’ at /usr/include/c++/14/bits/stl_uninitialized.h:779:44,
        inlined from ‘constexpr void std::vector<_Tp, _Alloc>::_M_default_append(size_type) [with _Tp = unsigned char; _Alloc = std::allocator<unsigned char>]’ at /usr/include/c++/14/bits/vector.tcc:863:35,
        inlined from ‘constexpr void std::vector<_Tp, _Alloc>::resize(size_type) [with _Tp = unsigned char; _Alloc = std::allocator<unsigned char>]’ at /usr/include/c++/14/bits/stl_vector.h:1016:21,
        inlined from ‘std::vector<T> ConsumeFixedLengthByteVector(FuzzedDataProvider&, size_t) [with B = unsigned char]’ at ./test/fuzz/util.h:305:24,
        inlined from ‘void crypto_common_fuzz_target(FuzzBufferType)’ at test/fuzz/crypto_common.cpp:22:101:
    /usr/include/c++/14/bits/stl_algobase.h:972:25: error: ‘void* __builtin_memset(void*, int, long unsigned int)’ writing 1 byte into a region of size 0 overflows the destination [-Werror=stringop-overflow=]
      972 |         __builtin_memset(__first, static_cast<unsigned char>(__tmp), __len);
          |         ~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## Patch
### configure.ac
```diff
@@ -457,15 +457,10 @@ if test "x$enable_werror" = "xyes"; then
   AX_CHECK_COMPILE_FLAG([-Werror=return-type], [], [ERROR_CXXFLAGS="$ERROR_CXXFLAGS -Wno-error=return-type"], [$CXXFLAG_WERROR],
                         [AC_LANG_SOURCE([[#include <cassert>
                                           int f(){ assert(false); }]])])
-  dnl -Wstringop-overread is broken in GCC 11.
-  AC_COMPILE_IFELSE(
-    [AC_LANG_PROGRAM([[]],
-         [[#if __GNUC__ == 11
-           #error -Wstringop-overread is broken in GCC 11
-           #endif
-          ]])],
-    [],
-    [ERROR_CXXFLAGS="$ERROR_CXXFLAGS -Wno-stringop-overread"])
+
+  dnl -Wstringop-overread and -Wstringop-overflow are broken in gcc
+  AX_CHECK_COMPILE_FLAG([-Wstringop-overread], [WARN_CXXFLAGS="$WARN_CXXFLAGS -Wno-stringop-overread"], [], [$CXXFLAG_WERROR])
+  AX_CHECK_COMPILE_FLAG([-Wstringop-overflow], [WARN_CXXFLAGS="$WARN_CXXFLAGS -Wno-stringop-overflow"], [], [$CXXFLAG_WERROR])
 fi
 
 if test "x$CXXFLAGS_overridden" = "xno"; then
```
