# [H] Apache HTTP Server: mod_dav_lock indirect lock crash

## Summary
Severity: High
Advisory: BIT-apache-2026-29169
Aliases: CVE-2026-29169
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-apache-2026-29169
Type: osv

## Affected
- Bitnami: `apache` — affected >=0 <2.4.67

## Details
A NULL pointer dereference in mod_dav_lock in Apache HTTP Server 2.4.66 and earlier may allow an attacker to crash the server with a malicious request.mod_dav_lock is not used internally by mod_dav or mod_dav_fs.

The only known use-case for mod_dav_lock was mod_dav_svn from Apache Subversion earlier than version 1.2.0.

Users are recommended to upgrade to version 2.4.66, which fixes this issue, or remove mod_dav_lock.

## References
- http://www.openwall.com/lists/oss-security/2026/05/04/20
- http://www.openwall.com/lists/oss-security/2026/05/05/12
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://nvd.nist.gov/vuln/detail/CVE-2026-29169
