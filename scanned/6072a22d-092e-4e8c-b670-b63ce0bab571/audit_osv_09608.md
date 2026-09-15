# [M] CVE-2017-1000382

## Summary
Severity: Medium
Advisory: CVE-2017-1000382
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-10-31
Source: https://osv.dev/vulnerability/CVE-2017-1000382
Type: osv

## Details
VIM version 8.0.1187 (and other versions most likely) ignores umask when creating a swap file ("[ORIGINAL_FILENAME].swp") resulting in files that may be world readable or otherwise accessible in ways not intended by the user running the vi binary.

## References
- http://security.cucumberlinux.com/security/details.php?id=120
- http://www.openwall.com/lists/oss-security/2017/10/31/1
