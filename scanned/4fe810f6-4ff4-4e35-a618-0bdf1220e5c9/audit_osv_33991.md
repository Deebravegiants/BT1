# [M] Libssh: double free vulnerability in libssh key export functions

## Summary
Severity: Medium
Advisory: CVE-2025-5351
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-07-04
Source: https://osv.dev/vulnerability/CVE-2025-5351
Type: osv

## Details
A flaw was found in the key export functionality of libssh. The issue occurs in the internal function responsible for converting cryptographic keys into serialized formats. During error handling, a memory structure is freed but not cleared, leading to a potential double free issue if an additional failure occurs later in the function. This condition may result in heap corruption or application instability in low-memory scenarios, posing a risk to system reliability where key export operations are performed.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://git.libssh.org/projects/libssh.git/
- https://access.redhat.com/errata/RHSA-2026:18683
- https://access.redhat.com/security/cve/CVE-2025-5351
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/5xxx/CVE-2025-5351.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-5351
- https://bugzilla.redhat.com/show_bug.cgi?id=2369367
