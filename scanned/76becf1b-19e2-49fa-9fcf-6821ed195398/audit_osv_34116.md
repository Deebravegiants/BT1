# [M] Firebird XDR Message Parsing NULL Pointer Dereference Denial-of-Service Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2025-54989
Aliases: GHSA-7qp6-hqxj-pjjp
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-08-15
Source: https://osv.dev/vulnerability/CVE-2025-54989
Type: osv

## Details
Firebird is a relational database. Prior to versions 3.0.13, 4.0.6, and 5.0.3, there is an XDR message parsing NULL pointer dereference denial-of-service vulnerability in Firebird. This specific flaw exists within the parsing of xdr message from client. It leads to NULL pointer dereference and DoS. This issue has been patched in versions 3.0.13, 4.0.6, and 5.0.3.

## References
- https://lists.debian.org/debian-lts-announce/2025/08/msg00021.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54989.json
- https://github.com/FirebirdSQL/firebird/security/advisories/GHSA-7qp6-hqxj-pjjp
- https://nvd.nist.gov/vuln/detail/CVE-2025-54989
- https://github.com/FirebirdSQL/firebird/issues/8554
- https://github.com/FirebirdSQL/firebird/commit/169da595f8693fc1a65a79c741724b1bc8db9f25
