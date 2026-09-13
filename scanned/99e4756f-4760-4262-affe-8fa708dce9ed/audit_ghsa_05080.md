# [C] golang.org/x/crypto vulnerable to infinite loop on large channel writes

## Summary
Severity: Critical
Advisory: GHSA-rm3j-f69w-wqmq
CVE: CVE-2026-39834
CWE: CWE-190
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-rm3j-f69w-wqmq
Type: github-advisory

## Affected
- Go: `golang.org/x/crypto` — affected >=0 <0.52.0

## Details
When writing data larger than 4GB in a single Write call on an SSH channel, an integer overflow in the internal payload size calculation caused the write loop to spin indefinitely, sending empty packets without making progress. The size comparison now uses int64 to prevent truncation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-39834
- https://cs.opensource.google/go/x/crypto
- https://go.dev/cl/781663
- https://go.dev/issue/79567
- https://groups.google.com/g/golang-announce/c/a082jnz-LvI
- https://pkg.go.dev/vuln/GO-2026-5020
