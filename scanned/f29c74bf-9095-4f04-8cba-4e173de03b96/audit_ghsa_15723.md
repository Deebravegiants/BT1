# [C] Volcano has insecure permissions

## Summary
Severity: Critical
Advisory: GHSA-5g3x-8g2v-r8x8
CVE: CVE-2024-36533
CWE: CWE-1259
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-24
Source: https://github.com/advisories/GHSA-5g3x-8g2v-r8x8
Type: github-advisory

## Affected
- Go: `github.com/volcano-sh/volcano` — affected >=0 <1.10.0-alpha.0
- Go: `volcano.sh/volcano` — affected >=0 <1.10.0-alpha.0

## Details
Insecure permissions in volcano v1.8.2 allows attackers to access sensitive data and escalate privileges by obtaining the service account's token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-36533
- https://github.com/volcano-sh/volcano/issues/3446
- https://github.com/volcano-sh/volcano/pull/3449
- https://github.com/volcano-sh/volcano/commit/55963f71c76cb85cea1cdb9582ea7d58cfbedcf8
- https://gist.github.com/HouqiyuA/a0e05a26ecc80bd970ac4649faecc930
- https://github.com/volcano-sh/volcano
- https://pkg.go.dev/vuln/GO-2024-3034
