# [M] Botan has a TLS 1.3 certificate authentication bypass

## Summary
Severity: Medium
Advisory: CVE-2026-34582
Aliases: GHSA-pxcj-9ppx-g86g
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-34582
Type: osv

## Details
Botan is a C++ cryptography library. Prior to version 3.11.1, the TLS 1.3 implementation allowed ApplicationData records to be processed prior to the Finished message being received. A server which is attempting to enforce client authentication via certificates can by bypassed by a client which entirely omits Certificate, CertificateVerify, and the Finished message and instead sends application data records. This vulnerability is fixed in 3.11.1.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-34582.json
- https://access.redhat.com/security/cve/CVE-2026-34582
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34582.json
- https://github.com/randombit/botan/security/advisories/GHSA-pxcj-9ppx-g86g
- https://nvd.nist.gov/vuln/detail/CVE-2026-34582
- https://bugzilla.redhat.com/show_bug.cgi?id=2456285
