# [M] Bytebase does not restrict low privilege user to access admin issues

## Summary
Severity: Medium
Advisory: GHSA-5rc4-v5mj-g8c4
CVE: CVE-2022-32169
CWE: CWE-732
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-09-29
Source: https://github.com/advisories/GHSA-5rc4-v5mj-g8c4
Type: github-advisory

## Affected
- Go: `github.com/bytebase/bytebase` — affected >=0.1.0

## Details
The `Bytebase` application does not restrict low privilege user to access `admin issues` for which an unauthorized user can view the `OPEN` and `CLOSED` issues by `Admin` and the affected endpoint is `/issue`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-32169
- https://github.com/bytebase/bytebase
- https://github.com/bytebase/bytebase/blob/1.0.4/frontend/src/store/modules/issue.ts#L108-#L187
- https://www.mend.io/vulnerability-database/CVE-2022-32169
