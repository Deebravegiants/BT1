# [C] CVE-2022-48337

## Summary
Severity: Critical
Advisory: CVE-2022-48337
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-02-20
Source: https://osv.dev/vulnerability/CVE-2022-48337
Type: osv

## Details
GNU Emacs through 28.2 allows attackers to execute commands via shell metacharacters in the name of a source-code file, because lib-src/etags.c uses the system C library function in its implementation of the etags program. For example, a victim may use the "etags -u *" command (suggested in the etags documentation) in a situation where the current working directory has contents that depend on untrusted input.

## References
- https://git.savannah.gnu.org/cgit/emacs.git/commit/?id=01a4035c869b91c153af9a9132c87adb7669ea1c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48337.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FLPQ4K6H2S5TY3L5UDN4K4B3L5RQJYQ6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/U6HDBUQNAH2WL4MHWCTUZLN7NGF7CHTK/
- https://nvd.nist.gov/vuln/detail/CVE-2022-48337
- https://www.debian.org/security/2023/dsa-5360
- https://lists.debian.org/debian-lts-announce/2023/05/msg00008.html
