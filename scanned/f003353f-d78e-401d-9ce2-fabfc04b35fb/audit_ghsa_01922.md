# [M] go.mongodb.org/mongo-driver improperly validates cstrings when marshalling Go objects into BSON

## Summary
Severity: Medium
Advisory: GHSA-f6mq-5m25-4r72
CVE: CVE-2021-20329
CWE: CWE-1287, CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-06-15
Source: https://github.com/advisories/GHSA-f6mq-5m25-4r72
Type: github-advisory

## Affected
- Go: `go.mongodb.org/mongo-driver` — affected >=0 <1.5.1

## Details
Specific cstrings input may not be properly validated in the MongoDB Go Driver when marshalling Go objects into BSON. A malicious user could use a Go object with specific string to potentially inject additional fields into marshalled documents. This issue affects all MongoDB GO Drivers up to (and including) 1.5.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20329
- https://github.com/mongodb/mongo-go-driver/pull/622
- https://github.com/mongodb/mongo-go-driver/commit/2aca31d5986a9e1c65a92264736de9fdc3b9b4ca
- https://github.com/mongodb/mongo-go-driver
- https://github.com/mongodb/mongo-go-driver/releases/tag/v1.5.1
- https://jira.mongodb.org/browse/GODRIVER-1923
- https://pkg.go.dev/vuln/GO-2021-0112
