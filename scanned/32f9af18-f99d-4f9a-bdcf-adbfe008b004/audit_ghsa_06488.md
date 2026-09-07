# [M] sigstore-go has a multi-log threshold bypass via single compromised log

## Summary
Severity: Medium
Advisory: GHSA-9vcr-p3rj-q5q6
CVE: CVE-2026-49834
CWE: CWE-345, CWE-347
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-07-09
Source: https://github.com/advisories/GHSA-9vcr-p3rj-q5q6
Type: github-advisory

## Affected
- Go: `github.com/sigstore/sigstore-go` — affected >=0 <1.2.0

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

A verifier configured with WithTransparencyLog(N>1) or WithSignedCertificateTimestamps(N>1) expected defense-in-depth against the compromise of a single log instance. However, threshold counting counted verified witnesses per-entry or per-validation-path rather than per-log-authority.

As a result, a single compromised transparency log could forge multiple entries with different indices, and a single compromised CT log could verify multiple times (either across multiple certificate chains or via multiple embedded SCTs), fully satisfying the multi-log threshold requirements and defeating the multi-log policy.

Note that this does not affect Cosign, as Cosign sets a threshold of 1.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

Upgrade to v1.1.5.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

There is no workaround, beyond relying on trusted logs.

## References
- https://github.com/sigstore/sigstore-go/security/advisories/GHSA-9vcr-p3rj-q5q6
- https://nvd.nist.gov/vuln/detail/CVE-2026-49834
- https://github.com/sigstore/sigstore-go/pull/633
- https://github.com/sigstore/sigstore-go/commit/dbb07e62623edd5b175fb9dd5a41dcb85a159207
- https://github.com/sigstore/sigstore-go
- https://github.com/sigstore/sigstore-go/releases/tag/v1.2.0
