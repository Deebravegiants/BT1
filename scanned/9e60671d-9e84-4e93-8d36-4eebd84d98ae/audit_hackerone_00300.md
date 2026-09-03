# [M] Crash (DoS) when parsing a hostile TIFF

## Summary
Severity: Medium (CVSS 6.5)
Program: Internet Bug Bounty
Weakness: Uncontrolled Resource Consumption
Reporter: aerodudrizzt
State: resolved
Disclosed: 2019-10-13T09:30:35.525Z
Source: https://hackerone.com/reports/195580

## Details
The issue was reported and resolved by PHP's security team:
* Ticket #73737: https://bugs.php.net/bug.php?id=73737
* Git Commit: http://git.php.net/?p=php-src.git;a=commit;h=1cda0d7c2ffb62d8331c64e703131d9cabdc03ea

The EXIF module in all PHP versions (5.6.9 and below, 7.1.0 and below) is vulnerable to a DoS attack when parsing a hostile EXIF file of type TIFF. Here are the technical details:
* File: ext\exif\exif.c
* Function:  exif_convert_any_to_int
* Vulnerable tag: TAG_FMT_SRATIONAL

The relevant code is:
```
	case TAG_FMT_SRATIONAL:
		s_den = php_ifd_get32s(4+(char *)value, motorola_intel);
		if (s_den == 0) {
			return 0;
		} else {
			return php_ifd_get32s(value, motorola_intel) / s_den;
		}
```
On intel chipsets this division can trigger an exception in this edge case: -1 / MIN_INT (see link: http://x86.renejeschke.de/html/file_module_x86_id_72.html):

When tested with a simple PHP script and a specially crafted TIFF file (with an .exif extension), it triggered the following segmentation fault:
```
<?php
	$e = exif_thumbnail("example_hostile.exif");
	echo "Loaded the exif picture\n";
?>
```

And here is the trace:
Program terminated with signal SIGFPE, Arithmetic exception.
```
#0  0xb4fd9d74 in ?? () from /usr/lib/php/20151012/exif.so
(gdb) bt
#0  0xb4fd9d74 in ?? () from /usr/lib/php/20151012/exif.so
#1  0xb4fdb11f in ?? () from /usr/lib/php/20151012/exif.so
#2  0xb4fdbd40 in ?? () from /usr/lib/php/20151012/exif.so
#3  0xb4fdbc11 in ?? () from /usr/lib/php/20151012/exif.so
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/195580_
