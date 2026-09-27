# [C] glot-code-runner RCE

## Summary
Severity: Critical
Advisory: GHSA-vj95-2f9q-x7h6
CVE: CVE-2018-15747
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vj95-2f9q-x7h6
Type: github-advisory

## Affected
- Go: `github.com/prasmussen/glot-code-runner` — affected >=0

## Details
The default configuration of glot-www through 2018-05-19 allows remote attackers to execute arbitrary code because glot-code-runner supports os.system within a "python" "files" "content" JSON file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-15747
- https://github.com/prasmussen/glot-code-runner/issues/15
- https://github.com/prasmussen/glot-code-runner
