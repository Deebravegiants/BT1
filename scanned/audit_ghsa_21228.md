# [H] Shoutrrr util package DoS via sending 2000, 4000, or 6000 character messages

## Summary
Severity: High
Advisory: GHSA-477v-w82m-634j
CVE: CVE-2022-25891
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-07-16
Source: https://github.com/advisories/GHSA-477v-w82m-634j
Type: github-advisory

## Affected
- Go: `github.com/containrrr/shoutrrr` — affected >=0 <0.6.0

## Details
The package `github.com/containrrr/shoutrrr/pkg/util` before 0.6.0 are vulnerable to Denial of Service (DoS) via the `util.PartitionMessage` function. Exploiting this vulnerability is possible by sending exactly 2000, 4000, or 6000 characters messages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25891
- https://github.com/containrrr/shoutrrr/issues/240
- https://github.com/containrrr/shoutrrr/pull/242
- https://github.com/containrrr/shoutrrr/commit/6a27056f9d7522a8b493216195cb7634bf4b5c42
- https://github.com/containrrr/shoutrrr
- https://github.com/containrrr/shoutrrr/releases/tag/v0.6.0
- https://pkg.go.dev/vuln/GO-2022-0528
- https://snyk.io/vuln/SNYK-GOLANG-GITHUBCOMCONTAINRRRSHOUTRRRPKGUTIL-2849059
