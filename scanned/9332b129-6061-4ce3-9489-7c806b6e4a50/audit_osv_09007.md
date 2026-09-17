# [C] CVE-2016-7398

## Summary
Severity: Critical
Advisory: CVE-2016-7398
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-06
Source: https://osv.dev/vulnerability/CVE-2016-7398
Type: osv

## Details
A type confusion vulnerability in the merge_param() function of php_http_params.c in PHP's pecl-http extension 3.1.0beta2 (PHP 7) and earlier as well as 2.6.0beta2 (PHP 5) and earlier allows attackers to crash PHP and possibly execute arbitrary code via crafted HTTP requests.

## References
- https://lists.debian.org/debian-lts-announce/2019/09/msg00022.html
- https://github.com/m6w6/ext-http/commit/17137d4ab1ce81a2cee0fae842340a344ef3da83
- https://bugs.php.net/bug.php?id=73055
- https://bugs.php.net/bug.php?id=73055&edit=1
