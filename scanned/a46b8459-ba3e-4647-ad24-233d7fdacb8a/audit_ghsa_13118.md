# [H] x/net/html Vulnerable to DoS During HTML Parsing

## Summary
Severity: High
Advisory: GHSA-vfw5-hrgq-h5wf
CVE: CVE-2018-17846
CWE: CWE-835
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-09-25
Source: https://github.com/advisories/GHSA-vfw5-hrgq-h5wf
Type: github-advisory

## Affected
- Go: `golang.org/x/net` — affected >=0 <0.0.0-20190125091013-d26f9f9a57f3

## Details
The html package (aka x/net/html) through 2018-09-25 in Go mishandles `<table><math><select><mi><select></table>`, leading to an infinite loop during an `html.Parse` call because `inSelectIM` and `inSelectInTableIM` do not comply with a specification.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-17846
- https://github.com/golang/go/issues/27842
- https://go-review.googlesource.com/c/137275
- https://go.dev/issue/27842
- https://go.googlesource.com/net/+/d26f9f9a57f3fab6a695bec0d84433c2c50f8bbf
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LREEWY6KNLHRWFZ7OT4HVLMVVCGGUHON
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UKRCI7WIOCOCD3H7NXWRGIRABTQOZOBK
- https://pkg.go.dev/vuln/GO-2020-0014
