# [C] Signature validation bypass in github.com/moov-io/signedxml

## Summary
Severity: Critical
Advisory: GHSA-jqvr-j2vg-gjrv
CVE: CVE-2023-34205
CWE: CWE-347
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-05-30
Source: https://github.com/advisories/GHSA-jqvr-j2vg-gjrv
Type: github-advisory

## Affected
- Go: `github.com/moov-io/signedxml` — affected >=0 <1.1.0

## Details
In Moov signedxml through 1.0.0, parsing the raw XML (as received) can result in different output than parsing the canonicalized XML. Thus, signature validation can be bypassed via a Signature Wrapping attack (aka XSW).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-34205
- https://github.com/moov-io/signedxml/issues/23
- https://github.com/moov-io/signedxml/pull/25
- https://github.com/moov-io/signedxml
- https://github.com/moov-io/signedxml/releases/tag/v1.1.0
- https://pkg.go.dev/vuln/GO-2023-1826
