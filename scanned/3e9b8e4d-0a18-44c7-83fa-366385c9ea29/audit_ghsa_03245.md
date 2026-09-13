# [H] Infinite Loop in jsonparser

## Summary
Severity: High
Advisory: GHSA-rmh2-65xw-9m6q
CVE: CVE-2020-10675
CWE: CWE-835
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-rmh2-65xw-9m6q
Type: github-advisory

## Affected
- Go: `github.com/buger/jsonparser` — affected >=0 <1.0.0

## Details
The Library API in buger jsonparser through 2019-12-04 allows attackers to cause a denial of service (infinite loop) via a Delete call.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10675
- https://github.com/buger/jsonparser/issues/188
- https://github.com/buger/jsonparser/pull/192
- https://github.com/buger/jsonparser/commit/91ac96899e492584984ded0c8f9a08f10b473717
- https://github.com/buger/jsonparser
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4C7PV6KEUUM76V4B2J5IFN2U6LEOWB67
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6KUHKDQSEYJNROA66OMN6AAQMGAAN6WI
- https://pkg.go.dev/vuln/GO-2021-0089
