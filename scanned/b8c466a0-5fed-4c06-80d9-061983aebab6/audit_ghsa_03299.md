# [H] Go JOSE Signature Validation Bypass

## Summary
Severity: High
Advisory: GHSA-77gc-fj98-665h
CVE: CVE-2016-9122
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-77gc-fj98-665h
Type: github-advisory

## Affected
- Go: `gopkg.in/square/go-jose.v1` — affected >=0 <1.1.0

## Details
Go JOSE before 1.1.0 suffers from multiple signatures exploitation. The go-jose library supports messages with multiple signatures. However, when validating a signed message the API did not indicate which signature was valid, which could potentially lead to confusion. For example, users of the library might mistakenly read protected header values from an attached signature that was different from the one originally validated

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-9122
- https://github.com/square/go-jose/pull/111
- https://github.com/square/go-jose/commit/2c5656adca9909843c4ff50acf1d2cf8f32da7e6
- https://github.com/square/go-jose/commit/789a4c4bd4c118f7564954f441b29c153ccd6a96
- https://github.com/square/go-jose/commit/c7581939a3656bb65e89d64da0a52364a33d2507
- https://hackerone.com/reports/169629
- https://github.com/square/go-jose
- https://www.openwall.com/lists/oss-security/2016/11/03/1
- http://www.openwall.com/lists/oss-security/2016/11/03/1
