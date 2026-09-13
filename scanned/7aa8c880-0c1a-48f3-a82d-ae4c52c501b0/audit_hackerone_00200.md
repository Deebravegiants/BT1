# [H] mb_strtolower (UTF-32LE): stack-buffer-overflow at php_unicode_tolower_full (CVE-2020-7065)

## Summary
Severity: High
Program: Internet Bug Bounty
Weakness: Stack Overflow
Reporter: anatoliq
State: resolved
Disclosed: 2020-10-21T07:56:56.251Z
CVE: CVE-2020-7065
Source: https://hackerone.com/reports/838127

## Details
PHP bug report (made public by the maintainers at the time of writing): https://bugs.php.net/bug.php?id=79371
Mitre CVE page: https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-7065
Link to the release notes: https://www.php.net/ChangeLog-7.php#7.4.4

## Impact

One of impacts is that the issue allows an attacker to straightforwardly crash the PHP interpreter provided a specific UTF character can be passed to `mb_strtolower` function dealing with UTF-32LE encoding. 

Original summary from the bug report:
> A call to `mb_strtolower` allows overwriting of a stack-allocated buffer with an overflown array from .rodata.

Description as provided by CVE database entry:
> In PHP versions 7.3.x below 7.3.16 and 7.4.x below 7.4.34, while using mb_strtolower() function with UTF-32LE encoding, certain invalid strings could cause PHP to overwrite stack-allocated buffer. This could lead to memory corruption, crashes and potentially code execution.
