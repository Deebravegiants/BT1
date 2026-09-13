# [H] golang.org/x/net/html Improper Validation of Array Index vulnerability

## Summary
Severity: High
Advisory: GHSA-mv93-wvcp-7m7r
CVE: CVE-2018-17848
CWE: CWE-129
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-mv93-wvcp-7m7r
Type: github-advisory

## Affected
- Go: `golang.org/x/net` — affected >=0 <0.0.0-20190125002852-4b62a64f59f7

## Details
The html package (aka `x/net/html`) through 2018-09-25 in Go mishandles <math><template><mn><b></template>, leading to a "panic: runtime error" (index out of range) in (*insertionModeStack).pop in node.go, called from inHeadIM, during an html.Parse call.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-17848
- https://github.com/golang/go/issues/27846
- https://go.dev/cl/159397
- https://go.dev/issue/27846
- https://go.googlesource.com/net/+/4b62a64f59f73840b9ab79204c94fee61cd1ba2c
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LREEWY6KNLHRWFZ7OT4HVLMVVCGGUHON
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UKRCI7WIOCOCD3H7NXWRGIRABTQOZOBK
- https://pkg.go.dev/vuln/GO-2022-0197
