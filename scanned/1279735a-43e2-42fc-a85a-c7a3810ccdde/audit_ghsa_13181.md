# [M] Kiali content spoofing vulnerability

## Summary
Severity: Medium
Advisory: GHSA-6f4m-j56w-55c3
CVE: CVE-2022-3962
CWE: CWE-74
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-09-23
Source: https://github.com/advisories/GHSA-6f4m-j56w-55c3
Type: github-advisory

## Affected
- Go: `github.com/kiali/kiali` — affected >=0 <1.57.4

## Details
A content spoofing vulnerability was found in Kiali. It was discovered that Kiali does not implement error handling when the page or endpoint being accessed cannot be found. This issue allows an attacker to perform arbitrary text injection when an error response is retrieved from the URL being accessed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3962
- https://github.com/kiali/kiali/commit/aab7694f850f04d7fd875fac5f720a93ccdf01ad
- https://access.redhat.com/errata/RHSA-2023:0542
- https://access.redhat.com/security/cve/CVE-2022-3962
- https://bugzilla.redhat.com/show_bug.cgi?id=2148661
- https://github.com/kiali/kiali
- https://issues.redhat.com/browse/OSSM-2251?attachmentViewMode=list
