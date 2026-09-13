# [H] CVE-2022-45939

## Summary
Severity: High
Advisory: CVE-2022-45939
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-11-28
Source: https://osv.dev/vulnerability/CVE-2022-45939
Type: osv

## Details
GNU Emacs through 28.2 allows attackers to execute commands via shell metacharacters in the name of a source-code file, because lib-src/etags.c uses the system C library function in its implementation of the ctags program. For example, a victim may use the "ctags *" command (suggested in the ctags documentation) in a situation where the current working directory has contents that depend on untrusted input.

## References
- https://git.savannah.gnu.org/cgit/emacs.git/commit/?id=d48bb4874bc6cd3e69c7a15fc3c91cc141025c51
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/45xxx/CVE-2022-45939.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FOSK3J7BBAEI4IITW2DRUKLQYUZYKH6Y/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GOXIH2FDEQJEAARE52C3GHTLGQFBYPIB/
- https://nvd.nist.gov/vuln/detail/CVE-2022-45939
- https://www.debian.org/security/2023/dsa-5314
- https://lists.debian.org/debian-lts-announce/2022/12/msg00046.html
