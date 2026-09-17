# [M] golang.org/x/text Infinite loop

## Summary
Severity: Medium
Advisory: GHSA-5rcv-m4m3-hfh7
CVE: CVE-2020-14040
CWE: CWE-400, CWE-835
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H/E:P/RL:O/RC:C (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-5rcv-m4m3-hfh7
Type: github-advisory

## Affected
- Go: `golang.org/x/text` — affected >=0 <0.3.3

## Details
Go version v0.3.3 of the x/text package fixes a vulnerability in encoding/unicode that could lead to the UTF-16 decoder entering an infinite loop, causing the program to crash or run out of memory. An attacker could provide a single byte to a UTF16 decoder instantiated with UseBOM or ExpectBOM to trigger an infinite loop if the String function on the Decoder is called, or the Decoder is passed to golang.org/x/text/transform.String.

### Specific Go Packages Affected
golang.org/x/text/encoding/unicode
golang.org/x/text/transform

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-14040
- https://github.com/golang/go/issues/39491
- https://github.com/golang/text/commit/23ae387dee1f90d29a23c0e87ee0b46038fbed0e
- https://go-review.googlesource.com/c/text/+/238238
- https://go.dev/cl/238238
- https://go.dev/issue/39491
- https://go.googlesource.com/text/+/23ae387dee1f90d29a23c0e87ee0b46038fbed0e
- https://groups.google.com/forum/#!topic/golang-announce/bXVeAmGOqz0
- https://groups.google.com/g/golang-announce/c/bXVeAmGOqz0
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TACQFZDPA7AUR6TRZBCX2RGRFSDYLI7O
