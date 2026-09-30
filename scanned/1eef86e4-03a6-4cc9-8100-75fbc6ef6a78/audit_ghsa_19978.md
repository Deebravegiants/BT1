# [M] usememos/memos missing Secure cookie attribute

## Summary
Severity: Medium
Advisory: GHSA-qcw2-492v-57xj
CVE: CVE-2022-4683
CWE: CWE-311, CWE-319, CWE-614
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-12-23
Source: https://github.com/advisories/GHSA-qcw2-492v-57xj
Type: github-advisory

## Affected
- Go: `github.com/usememos/memos` — affected >=0 <0.9.0

## Details
usememos/memos is an open-source, self-hosted memo hub with knowledge management and socialization. Memos prior to 0.9.0 is missing the Secure cookie attribute, making it vulnerable to session hijacking.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4683
- https://github.com/usememos/memos/commit/7efa749c6628c75b19a912ca170529f5c293bb2e
- https://github.com/usememos/memos
- https://huntr.dev/bounties/84973f6b-739a-4d7e-8757-fc58cbbaf6ef
