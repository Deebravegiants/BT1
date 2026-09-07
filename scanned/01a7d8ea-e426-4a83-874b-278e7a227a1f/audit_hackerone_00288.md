# [H] Stack Buffer Overflow in GD dynamicGetbuf

## Summary
Severity: High
Program: Internet Bug Bounty
Weakness: Memory Corruption - Generic
Reporter: libnex
State: resolved
Disclosed: 2019-11-12T09:26:14.063Z
Source: https://hackerone.com/reports/175587

## Details
#Stack-based buffer over flow in GD dynamicGetbuf#
- Vulnerable function: imagecreatefromstring()
- Bug has been reported: https://bugs.php.net/bug.php?id=73280
- Submitted a patch and accepted: https://github.com/php/php-src/commit/cc08cbc84d46933c1e9e0149633f1ed5d19e45e9
- Impact: Remotely Exploitable. Given the nature of the function, it is not uncommon to see programmers passing user inputs to the vulnerable function imagecreatefromstring(). Real life examples:
  * https://github.com/rbloone/sslv-scraper/blob/305c79e24421795abdae8106ad686cb9c6742e94/img.php
  * https://github.com/hick/utl/blob/a573f04ac0a6db2cfe56e2785dfab7b1534c04f3/pasteimage/file.php

Description:
------------
1) imagecreatefromstring() takes in a string and attempts to convert it into an image. The string is in the variable "data" and the length is stored as size_t (unsigned) within a zend_string structure as seen below. When passed into gdNewDynamicCtxEx(), it gets converted implicitly into an int (signed). If the MSB of the size_t is 1, when converting to an int, this becomes a negative number.

_php_image_create_from_string(...) at php-7.0.11/ext/gd/gd.c:2227
	
```c
2227                 io_ctx = gdNewDynamicCtxEx(Z_STRLEN_P(data), Z_STRVAL_P(data), 0);
```

2) Tracing the code deeper, the size is set to dp (dynamicPtr) below

allocDynamic(...) at ext/gd/libgd/gd_io_dp.c:272
```c
280                 dp->logicalSize = initialSize;
```



3) During the image conversion, dynamicGetchar() gets called to read 1 byte (line 257).

dynamicGetchar(..) at ext/gd/libgd/gd_io_dp.c
```c
	254             unsigned char b;
	255             int rv;
	256
	257             rv = dynamicGetbuf (ctx, &b, 1);
```



_Trimmed to 38 lines — full report: https://hackerone.com/reports/175587_
