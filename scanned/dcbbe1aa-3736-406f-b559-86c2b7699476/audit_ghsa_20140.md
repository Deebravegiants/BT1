# [M] YAML Go package vulnerable to denial of service

## Summary
Severity: Medium
Advisory: GHSA-r88r-gmrh-7j83
CVE: CVE-2021-4235
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-12-28
Source: https://github.com/advisories/GHSA-r88r-gmrh-7j83
Type: github-advisory

## Affected
- Go: `gopkg.in/yaml.v2` — affected >=0 <2.2.3
- Go: `github.com/go-yaml/yaml` — affected >=0

## Details
Due to unbounded alias chasing, a maliciously crafted YAML file can cause the system to consume significant system resources. If parsing user input, this may be used as a denial of service vector.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4235
- https://github.com/go-yaml/yaml/pull/375
- https://github.com/go-yaml/yaml/commit/bb4e33bf68bf89cad44d386192cbed201f35b241
- https://github.com/go-yaml/yaml
- https://lists.debian.org/debian-lts-announce/2023/07/msg00001.html
- https://pkg.go.dev/vuln/GO-2021-0061
