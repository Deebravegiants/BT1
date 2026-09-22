# [C] Authentication Bypass when using using older password hashes

## Summary
Severity: Critical
Advisory: CVE-2024-34340
Aliases: GHSA-37x7-mfjv-mm7m
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-05-13
Source: https://osv.dev/vulnerability/CVE-2024-34340
Type: osv

## Details
Cacti provides an operational monitoring and fault management framework. Prior to version 1.2.27, Cacti calls `compat_password_hash` when users set their password. `compat_password_hash` use `password_hash` if there is it, else use `md5`. When verifying password, it calls `compat_password_verify`. In `compat_password_verify`, `password_verify` is called if there is it, else use `md5`. `password_verify` and `password_hash` are supported on PHP < 5.5.0, following PHP manual. The vulnerability is in `compat_password_verify`. Md5-hashed user input is compared with correct password in database by `$md5 == $hash`. It is a loose comparison, not `===`. It is a type juggling vulnerability. Version 1.2.27 contains a patch for the issue.

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00027.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RBEOAFKRARQHTDIYSL723XAFJ2Q6624X/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34340.json
- https://github.com/Cacti/cacti/security/advisories/GHSA-37x7-mfjv-mm7m
- https://nvd.nist.gov/vuln/detail/CVE-2024-34340
