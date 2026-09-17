# [M] Libssh: null pointer dereference in libssh kex session id calculation

## Summary
Severity: Medium
Advisory: CVE-2025-8114
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-07-24
Source: https://osv.dev/vulnerability/CVE-2025-8114
Type: osv

## Details
A flaw was found in libssh, a library that implements the SSH protocol. When calculating the session ID during the key exchange (KEX) process, an allocation failure in cryptographic functions may lead to a NULL pointer dereference. This issue can cause the client or server to crash.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://git.libssh.org/projects/libssh.git/
- https://git.libssh.org/projects/libssh.git/commit/?id=53ac23ded4cb2c5463f6c4cd1525331bd578812d
- https://git.libssh.org/projects/libssh.git/commit/?id=65f363c9
- https://access.redhat.com/errata/RHSA-2026:18683
- https://access.redhat.com/security/cve/CVE-2025-8114
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/8xxx/CVE-2025-8114.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-8114
- https://www.libssh.org/security/advisories/CVE-2025-8114.txt
- https://bugzilla.redhat.com/show_bug.cgi?id=2383220
