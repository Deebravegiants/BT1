# [C] CVE-2018-1000533

## Summary
Severity: Critical
Advisory: CVE-2018-1000533
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-26
Source: https://osv.dev/vulnerability/CVE-2018-1000533
Type: osv

## Details
klaussilveira GitList version <= 0.6 contains a Passing incorrectly sanitized input to system function vulnerability in `searchTree` function that can result in Execute any code as PHP user. This attack appear to be exploitable via Send POST request using search form. This vulnerability appears to have been fixed in 0.7 after commit 87b8c26b023c3fc37f0796b14bb13710f397b322.

## References
- https://github.com/klaussilveira/gitlist/commit/87b8c26b023c3fc37f0796b14bb13710f397b322
- https://security.szurek.pl/exploit-bypass-php-escapeshellarg-escapeshellcmd.html
