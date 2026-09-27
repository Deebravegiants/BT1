# [M] Libssh: incorrect return code handling in ssh_kdf() in libssh

## Summary
Severity: Medium
Advisory: CVE-2025-5372
CVSS: 5.0 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-07-04
Source: https://osv.dev/vulnerability/CVE-2025-5372
Type: osv

## Details
A flaw was found in libssh versions built with OpenSSL versions older than 3.0, specifically in the ssh_kdf() function responsible for key derivation. Due to inconsistent interpretation of return values where OpenSSL uses 0 to indicate failure and libssh uses 0 for success—the function may mistakenly return a success status even when key derivation fails. This results in uninitialized cryptographic key buffers being used in subsequent communication, potentially compromising SSH sessions' confidentiality, integrity, and availability.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2025:21977
- https://access.redhat.com/errata/RHSA-2025:23024
- https://access.redhat.com/errata/RHSA-2026:20610
- https://access.redhat.com/errata/RHSA-2026:24349
- https://access.redhat.com/errata/RHSA-2026:25911
- https://access.redhat.com/security/cve/CVE-2025-5372
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/5xxx/CVE-2025-5372.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-5372
- https://bugzilla.redhat.com/show_bug.cgi?id=2369388
- https://git.libssh.org/projects/libssh.git
