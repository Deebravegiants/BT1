# [H] Golang FIPS OpenSSL has a Use of Uninitialized Variable vulnerability

## Summary
Severity: High
Advisory: GHSA-3h3x-2hwv-hr52
CVE: CVE-2024-9355
CWE: CWE-457
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2024-10-01
Source: https://github.com/advisories/GHSA-3h3x-2hwv-hr52
Type: github-advisory

## Affected
- Go: `github.com/golang-fips/openssl` — affected >=0

## Details
A vulnerability was found in Golang FIPS OpenSSL. This flaw allows a malicious user to randomly cause an uninitialized buffer length variable with a zeroed buffer to be returned in FIPS mode. It may also be possible to force a false positive match between non-equal hashes when comparing a trusted computed hmac sum to an untrusted input sum if an attacker can send a zeroed buffer in place of a pre-computed sum.  It is also possible to force a derived key to be all zeros instead of an unpredictable value.  This may have follow-on implications for the Go TLS stack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-9355
- https://github.com/golang-fips/openssl/pull/198
- https://github.com/github/advisory-database/pull/4950
- https://pkg.go.dev/vuln/GO-2024-3167
- https://github.com/golang-fips/openssl
- https://bugzilla.redhat.com/show_bug.cgi?id=2315719
- https://access.redhat.com/security/cve/CVE-2024-9355
- https://access.redhat.com/errata/RHSA-2026:59439
- https://access.redhat.com/errata/RHSA-2026:55525
- https://access.redhat.com/errata/RHSA-2026:55520
- https://access.redhat.com/errata/RHSA-2025:7624
- https://access.redhat.com/errata/RHSA-2025:7256
- https://access.redhat.com/errata/RHSA-2025:7118
- https://access.redhat.com/errata/RHSA-2025:2416
- https://access.redhat.com/errata/RHSA-2024:9551
- https://access.redhat.com/errata/RHSA-2024:8847
- https://access.redhat.com/errata/RHSA-2024:8678
- https://access.redhat.com/errata/RHSA-2024:8327
- https://access.redhat.com/errata/RHSA-2024:7550
- https://access.redhat.com/errata/RHSA-2024:7502
