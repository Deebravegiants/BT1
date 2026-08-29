# [M] Int Overflow lead to Heap OverFlow in exif_thumbnail_extract of exif.c

## Summary
Severity: Medium (CVSS 5.3)
Program: Internet Bug Bounty
Weakness: Integer Overflow
Reporter: md4
State: resolved
Disclosed: 2019-10-21T05:19:46.535Z
CVE: CVE-2018-14883
Source: https://hackerone.com/reports/384477

## Details
This bug was reported to PHP last month and a fix was public last week:https://bugs.php.net/bug.php?id=76423
Heap OverFlow in exif_thumbnail_extract of exif.c
This vulnerability can be triggered by exif_read_data in any 32-bit system.
exif.c:2947:
```
if ((ImageInfo->Thumbnail.offset + ImageInfo->Thumbnail.size) > length) {
	EXIF_ERRLOG_THUMBEOF(ImageInfo)
	return;
}
ImageInfo->Thumbnail.data = estrndup(offset + ImageInfo->Thumbnail.offset, ImageInfo->Thumbnail.size);
```

`ImageInfo->Thumbnail.offset` is in range(0xffffffff) and `ImageInfo->Thumbnail.size` is in range(0xffff). In 32 bit system, `ImageInfo->Thumbnail.offset + ImageInfo->Thumbnail.size` can be an int overflow, which can bypass the check of length and lead to heap overflow in `estrndup`.


Test script:
---------------
https://gist.github.com/yough3rt/f03920196a3bb9cec03e08e02079309a

USE_ZEND_ALLOC=0 /home/youghurt/php-llvm/bin/php IDF_tag.php



Expected result:
----------------
No Error.

Actual result:
--------------
```
When running the test script with an ASAN enabled PHP interpreter with USE_ZEND_ALLOC=0, the following ASAN report/backtrace is generated:
=================================================================
==29132==ERROR: AddressSanitizer: heap-buffer-overflow on address 0xb2500000 at pc 0x0814a6cd bp 0xbfd1f388 sp 0xbfd1ef60
READ of size 65535 at 0xb2500000 thread T0
    #0 0x814a6cc in __asan_memcpy /home/youghurt/llvm-src/projects/compiler-rt/lib/asan/asan_interceptors_memintrinsics.cc:23
    #1 0x95f1eaa in _estrndup /home/youghurt/php-7.2.6/Zend/zend_alloc.c:2538:2
    #2 0x899a435 in exif_thumbnail_extract /home/youghurt/php-7.2.6/ext/exif/exif.c:2951:30
    #3 0x899665e in exif_process_IFD_in_JPEG /home/youghurt/php-7.2.6/ext/exif/exif.c:3619:5
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/384477_
