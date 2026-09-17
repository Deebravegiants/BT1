# [M] CVE-2010-3359

## Summary
Severity: Medium
Advisory: CVE-2010-3359
CVSS: 4.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2019-11-12
Source: https://osv.dev/vulnerability/CVE-2010-3359
Type: osv

## Details
If LD_LIBRARY_PATH is undefined in gargoyle-free before 2009-08-25, the variable will point to the current directory. This can allow a local user to trick another user into running gargoyle in a directory with a cracked libgarglk.so and gain access to the user's account.

## References
- https://security-tracker.debian.org/tracker/CVE-2010-3359
