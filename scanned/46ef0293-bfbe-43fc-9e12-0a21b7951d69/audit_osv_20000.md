# [M] CVE-2021-29157

## Summary
Severity: Medium
Advisory: CVE-2021-29157
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-06-28
Source: https://osv.dev/vulnerability/CVE-2021-29157
Type: osv

## Details
Dovecot before 2.3.15 allows ../ Path Traversal. An attacker with access to the local filesystem can trick OAuth2 authentication into using an HS256 validation key from an attacker-controlled location. This occurs during use of local JWT validation with the posix fs driver.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JB2VTJ3G2ILYWH5Y2FTY2PUHT2MD6VMI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TK424DWFO2TKJYXZ2H3XL633TYJL4GQN/
- https://dovecot.org/security
- https://security.gentoo.org/glsa/202107-41
- https://www.openwall.com/lists/oss-security/2021/06/28/1
