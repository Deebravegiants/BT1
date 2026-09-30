# [M] Libssh: libssh: integrity downgrade via openssl aes-gcm tag verification

## Summary
Severity: Medium
Advisory: CVE-2026-59847
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-59847
Type: osv

## Details
A flaw was found in libssh. Incorrect AES-GCM finalization checks in builds using the OpenSSL backend can effectively remove integrity protection, allowing an in-path attacker to modify plaintext on the wire without detection.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/errata/RHSA-2026:42922
- https://access.redhat.com/errata/RHSA-2026:55855
- https://access.redhat.com/errata/RHSA-2026:62217
- https://access.redhat.com/errata/RHSA-2026:62218
- https://access.redhat.com/security/cve/CVE-2026-59847
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59847.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59847
- https://bugzilla.redhat.com/show_bug.cgi?id=2498180
